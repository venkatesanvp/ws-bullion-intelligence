"""Real PostgreSQL research contract tests, SYNTHETIC_TEST only. WI-07/08/10."""

from datetime import date, timedelta
import pytest
from app import research
from .test_integration import seed, upload, history

CSV = "trading_date,close\n2026-01-01,10\n2026-01-02,12\n2026-01-03,14\n2026-01-04,13\n"


def indicator(api, meta, method="EMA", n=2, **options):
    return api.get(
        "/api/v1/instruments/" + meta["instrument_id"] + "/indicators",
        params={
            "source_id": meta["source_id"],
            "basis": meta["price_basis"],
            "indicator": method,
            "n": n,
            **options,
        },
    )


def chart(api, meta, **options):
    return api.get(
        "/api/v1/instruments/" + meta["instrument_id"] + "/chart",
        params={"source_id": meta["source_id"], "basis": meta["price_basis"], **options},
    )


def compare(api, *metadata, **options):
    return api.post(
        "/api/v1/comparisons",
        json={
            "series": [
                {
                    "instrument_id": m["instrument_id"],
                    "source_id": m["source_id"],
                    "price_basis": m["price_basis"],
                }
                for m in metadata
            ],
            "start": "2026-01-01",
            "end": "2026-01-04",
            **options,
        },
    )


def test_chart_exact_prices_and_indicator_prefix_metadata(api):
    _, _, meta = seed(api)
    assert upload(api, meta, CSV).status_code == 201
    price = chart(api, meta).json()
    assert len(price["data"]["points"]) == 4
    assert price["data"]["points"][0]["close"] == "10.0000000000"
    assert price["meta"]["source"]["data_class"] == "SYNTHETIC_TEST"
    full = indicator(api, meta, end="2026-01-04").json()
    assert full["data"]["values"][-1]["value"] == "13.000000000000"
    assert full["data"]["seed_date"] == "2026-01-02"
    assert full["data"]["window_unit"] == "OBSERVED_BARS"
    assert full["meta"]["quality"]["continuity"] == "UNVERIFIED"
    restricted = indicator(api, meta, start="2026-01-03", end="2026-01-04").json()
    assert restricted["data"]["values"] == full["data"]["values"][2:]
    assert restricted["data"]["input_fingerprint"] == full["data"]["input_fingerprint"]
    repeated = indicator(api, meta, end="2026-01-04").json()
    assert repeated["data"]["input_fingerprint"] == full["data"]["input_fingerprint"]
    assert upload(api, meta, "trading_date,close\n2026-01-05,99\n").status_code == 201
    assert indicator(api, meta, end="2026-01-04").json()["data"]["values"] == full["data"]["values"]


@pytest.mark.parametrize("kind", ["gap", "action"])
def test_known_discontinuity_resets_and_chart_breaks(api, kind):
    profile = (
        {"known_break_dates": ["2026-01-03"]}
        if kind == "action"
        else {
            "calendar": {
                "evidence_ref": "SYNTHETIC TEST",
                "version": "test",
                "coverage_start": "2026-01-01",
                "coverage_end": "2026-01-05",
                "session_dates": [
                    "2026-01-01",
                    "2026-01-02",
                    "2026-01-03",
                    "2026-01-04",
                    "2026-01-05",
                ],
            }
        }
    )
    _, _, meta = seed(api, profile=profile)
    csv = CSV if kind == "action" else CSV.replace("2026-01-03,14\n", "") + "2026-01-05,15\n"
    assert upload(api, meta, csv).status_code == 201
    result = indicator(api, meta).json()["data"]["values"]
    boundary = 2
    assert result[boundary]["value"] is None and result[boundary]["reason"] == "DISCONTINUITY"
    assert chart(api, meta).json()["data"]["points"][boundary]["break_before"]
    assert result[-1]["seed_date"] == ("2026-01-04" if kind == "action" else "2026-01-05")


@pytest.mark.parametrize(
    "method,n", [("RSI", 1), ("SMA", 0), ("EMA", 10001), ("RSI", "true"), ("SMA", "2.5")]
)
def test_invalid_lookbacks(api, method, n):
    _, _, meta = seed(api)
    assert indicator(api, meta, method, n).status_code == 422


def test_empty_short_and_unknown_basis(api):
    _, _, meta = seed(api)
    assert chart(api, meta).json()["data"]["unavailable_reason"] == "NO_HISTORY"
    assert indicator(api, meta).json()["data"]["unavailable_reason"] == "NO_HISTORY"
    assert upload(api, meta, CSV[: CSV.index("2026-01-03")]).status_code == 201
    assert (
        indicator(api, meta, "RSI", 3).json()["data"]["unavailable_reason"]
        == "INSUFFICIENT_HISTORY"
    )
    unknown = {**meta, "price_basis": "UNKNOWN"}
    assert upload(api, unknown, CSV).status_code == 201
    response = indicator(api, unknown)
    assert response.status_code == 422 and response.json()["error"]["code"] == "BASIS_UNVERIFIED"
    assert all(v["value"] is None for v in response.json()["data"]["values"])
    assert chart(api, unknown).status_code == 200


def test_comparison_common_dates_fingerprints_and_unknown_volume(api):
    _, _, a = seed(api)
    _, _, b = seed(api, symbol="SYNTH_SILVER")
    assert upload(api, a, CSV).status_code == 201
    assert upload(api, b, "trading_date,close\n2026-01-01,20\n2026-01-03,23\n").status_code == 201
    response = compare(api, a, b)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["common_dates"] == ["2026-01-01", "2026-01-03"]
    assert [s["price_change_percent"] for s in data["series"]] == [
        "40.000000000000",
        "15.000000000000",
    ]
    assert data["series"][1]["volume_end"] is None
    assert "PRICE_ONLY_NOT_TOTAL_RETURN" in data["limitations"]
    assert compare(api, a, b).json()["data"]["input_fingerprint"] == data["input_fingerprint"]
    assert (
        compare(api, a, b, start="2026-01-02").json()["data"]["unavailable_reason"]
        == "INSUFFICIENT_COMMON_DATES"
    )
    assert (
        compare(api, a, b, start="2026-01-04").json()["data"]["unavailable_reason"]
        == "NO_COMMON_DATES"
    )
    assert compare(api, a, a).status_code == 422
    assert compare(api, a, b, start="2026-01-05").status_code == 422


def test_incompatible_basis_and_unqualified_source(api):
    _, _, a = seed(api)
    _, _, b = seed(api, symbol="SYNTH_OTHER")
    b = {**b, "price_basis": "UNKNOWN"}
    response = compare(api, a, b)
    assert (
        response.status_code == 422
        and response.json()["data"]["unavailable_reason"] == "BASIS_UNVERIFIED"
    )
    _, _, unqualified = seed(api, symbol="SYNTH_UNQUALIFIED", qualified=False)
    assert indicator(api, unqualified).status_code == 403
    assert chart(api, unqualified).status_code == 403
    assert compare(api, a, unqualified).status_code == 403


def test_research_range_limits_do_not_truncate(api):
    _, _, meta = seed(api)
    first = date(2026, 1, 1)
    csv = "trading_date,close\n" + "".join(
        f"{first + timedelta(days=i)},10\n" for i in range(10001)
    )
    assert upload(api, meta, csv).status_code == 201
    for response in [chart(api, meta), indicator(api, meta)]:
        assert (
            response.status_code == 422
            and response.json()["error"]["code"] == "ANALYTICS_RANGE_LIMIT"
        )
    assert (
        len(chart(api, meta, start=str(first + timedelta(days=9999))).json()["data"]["points"]) == 2
    )
    assert indicator(api, meta, start=str(first + timedelta(days=9999))).status_code == 422


def test_comparison_uses_one_database_snapshot(api, monkeypatch):
    _, _, a = seed(api)
    _, _, b = seed(api, symbol="SYNTH_SECOND")
    assert upload(api, a).status_code == upload(api, b).status_code == 201
    original = research.bounded_points
    written = False

    def concurrent_append(db, *args, **kwargs):
        nonlocal written
        result = original(db, *args, **kwargs)
        if not written:
            written = True
            assert upload(api, b, "trading_date,close\n2026-01-03,99\n").status_code == 201
        return result

    monkeypatch.setattr(research, "bounded_points", concurrent_append)
    response = compare(api, a, b)
    assert response.status_code == 200, response.text
    second = response.json()["data"]["series"][1]["meta"]
    assert second["series_ref"]["revision"] == 1 and second["coverage"]["count"] == 2
    assert history(api, b).json()["meta"]["series_ref"]["revision"] == 2


def test_new_routes_require_local_auth(api_no_db):
    assert (
        api_no_db.get("/api/v1/instruments/00000000-0000-0000-0000-000000000000/chart").status_code
        == 401
    )
    assert api_no_db.post("/api/v1/comparisons", json={}).status_code == 401


def test_flat_rsi_is_explicitly_unavailable_after_seeding(api):
    _, _, metadata = seed(api)
    assert (
        upload(
            api,
            metadata,
            "trading_date,close\n2026-01-01,10\n2026-01-02,10\n2026-01-03,10\n2026-01-04,10\n",
        ).status_code
        == 201
    )
    result = indicator(api, metadata, "RSI", 2).json()["data"]
    assert result["status"] == "UNAVAILABLE" and result["unavailable_reason"] == "FLAT_WINDOW"
    assert result["values"][-1]["reason"] == "FLAT_WINDOW"
    assert all(value["value"] is None for value in result["values"])
