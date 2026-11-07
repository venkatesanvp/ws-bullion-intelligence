"""Package 2 read-only integration and provenance tests, all synthetic."""

from datetime import date, datetime
from fastapi.testclient import TestClient
from app.main import create_app
from app.technical_analytics import TechnicalParameters
from app.analytics import indicator_values
from .conftest import test_settings as settings_for_technical, TOKEN, ORIGIN
from .provider_fixtures import plan, collected
from .session_fixtures import provider_for_session, NOW
from app.transient_uat import NAMES


def install(db_engine):
    p = plan(date(2026, 9, 1), date(2026, 11, 6))
    provider, calls = provider_for_session()
    app = create_app(
        settings_for_technical(
            db_engine.url.render_as_string(hide_password=False),
            market_data_enabled=True,
            market_quotes_enabled=True,
            market_intraday_enabled=True,
        ),
        market_provider=provider,
        market_calendar=p.calendar,
    )
    _, data, _ = collected(p)
    app.state.transient_research.install(data, p, names=NAMES, data_class="SYNTHETIC_TEST")
    i = app.state.transient_research.listings()[0]
    s = app.state.transient_research.sources()[0]
    return app, i, s, calls


def test_daily_composite_snapshot_reuses_canonical_indicators_and_never_writes(
    db_engine, monkeypatch
):
    # Fixed fixture dates require the declared fixture clock, not the execution day.
    class FixtureClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr("app.technical_research.datetime", FixtureClock)
    app, i, s, calls = install(db_engine)
    store = app.state.transient_research
    before = store.rows(i.id, s.id, "PROVIDER_ADJUSTED")
    body = {"instrument_id": str(i.id), "source_id": str(s.id), "basis": "PROVIDER_ADJUSTED"}
    with TestClient(app, headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}) as client:
        response = client.post("/api/v1/research/technical", json=body)
        assert response.status_code == 200, response.text
        result = response.json()["data"]
        assert result["candles"] and result["excluded_incomplete_daily_rows"] == 1
        assert (
            result["parameters"]["atr_n"] == 14
            and result["indicators"]["MACD"]["values"][33]["signal"] is not None
        )
        points = store.points(i.id, s.id, "PROVIDER_ADJUSTED", end=date(2026, 11, 5))
        expected = indicator_values(points, "RSI", 14)
        assert [v["value"] for v in result["indicators"]["RSI"]["values"]] == [
            v["value"] for v in expected
        ]
        assert (
            client.post("/api/v1/research/technical", json=body).json()["data"]["input_fingerprint"]
            == result["input_fingerprint"]
        )
        selected = client.post(
            "/api/v1/research/technical", json={**body, "start": "2026-10-26"}
        ).json()["data"]
        assert (
            selected["warmup_bars"] > 0
            and selected["indicators"]["ATR"]["values"][0]["value"] is not None
        )
        assert (
            client.post("/api/v1/research/technical", json={**body, "basis": "UNKNOWN"}).status_code
            == 422
        )
        assert (
            client.post(
                "/api/v1/research/technical", json={**body, "parameters": {"macd_fast": 26}}
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/api/v1/research/technical",
                json={**body, "start": "2026-11-05", "end": "2026-10-01"},
            ).status_code
            == 422
        )
    assert store.rows(i.id, s.id, "PROVIDER_ADJUSTED") == before and not calls


def test_intraday_extension_uses_completed_bars_and_preserves_provenance():
    from .test_market_session import setup

    app, service, calls, _ = setup()
    i = service.daily.store.listings()[0]
    result = service.intraday(
        i.id,
        5,
        "current",
        indicators={"SMA": 20, "EMA": 37, "RSI": 14},
        technical=TechnicalParameters(),
    )
    assert result["technical"] and result["input_fingerprint"] and result["computed_at"]
    forming = {
        r["start"] for r in result["candles"] if r["classification"] == "INTRADAY_PROVISIONAL"
    }
    assert forming and not forming & {v["time"] for v in result["technical"]["ATR"]["values"]}
    assert result["warmup_bars"] >= 34
    assert any(v["histogram"] is not None for v in result["technical"]["MACD"]["values"])
    before = len(calls)
    repeat = service.intraday(i.id, 5, "current", technical=TechnicalParameters())
    assert len(calls) == before and repeat["input_fingerprint"] == result["input_fingerprint"]
    assert all(r.source_timestamp for rows in service.candles.values() for r in rows.values())


def test_technical_endpoint_authentication_and_sanitized_validation(api_no_db):
    assert api_no_db.post("/api/v1/research/technical", json={}).status_code == 401
    r = api_no_db.post(
        "/api/v1/research/technical",
        json={"access_token": "synthetic-sensitive-value"},
        headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN},
    )
    assert r.status_code in {422, 503} and "synthetic-sensitive-value" not in r.text
