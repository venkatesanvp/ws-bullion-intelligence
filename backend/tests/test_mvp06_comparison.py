"""MVP06 descriptive comparison qualification, arithmetic and source-boundary tests."""

from dataclasses import replace
from datetime import timedelta
from decimal import Decimal, localcontext, Context, ROUND_HALF_EVEN, getcontext, ROUND_DOWN
from types import SimpleNamespace
from fastapi.testclient import TestClient
import pytest
from app.comparison import compare_series
from app.main import get_db
from app.market_cache_transfer import export_cache
from app.forecast_research_service import display_changes
from .test_comparison import START, END, series
from .test_market_session import setup
from .provider_fixtures import collected
from .conftest import TOKEN, ORIGIN


def test_reference_normalization_drawdown_and_sample_volatility():
    days = tuple(START + timedelta(days=i) for i in range(3))
    a = replace(series("gold", [100, 120, 90]), calendar_sessions=days)
    b = replace(series("silver", [200, 240, 180]), calendar_sessions=days)
    result = compare_series([a, b], START, END)
    for s in result["series"]:
        assert s["price_change_percent"] == "-10.000000000000"
        assert s["maximum_drawdown_percent"] == "25.000000000000"
        assert [p["rebased_price"] for p in s["values"]] == [
            "100.000000000000",
            "120.000000000000",
            "90.000000000000",
        ]
        with localcontext(Context(prec=60, rounding=ROUND_HALF_EVEN)):
            expected = (Decimal("0.10125").sqrt() * 100).quantize(Decimal("0.000000000001"))
        assert Decimal(s["volatility_percent"]) == expected
    assert result["volatility_return_count"] == 2
    assert "NOT_ANNUALIZED" in result["volatility_convention"]


@pytest.mark.parametrize(
    "calendar", [None, (), (START, START + timedelta(days=1), START + timedelta(days=2))]
)
def test_sparse_intersection_does_not_invent_session_returns(calendar):
    a = replace(series("a", [10, 11, 12]), calendar_sessions=calendar)
    b = replace(series("b", [20, 23], days=(0, 2)), calendar_sessions=calendar)
    r = compare_series([a, b], START, END)
    assert r["common_observation_count"] == 2 and r["volatility_return_count"] == 0
    assert all(s["volatility_percent"] is None for s in r["series"])
    assert r["series"][0]["price_change_percent"] == "20.000000000000"


def test_volatility_requires_adjacency_in_both_calendars():
    a = replace(
        series("a", [10, 11, 12]),
        calendar_sessions=tuple(START + timedelta(days=i) for i in range(3)),
    )
    b = replace(
        series("b", [20, 22, 24]),
        calendar_sessions=(
            START,
            START + timedelta(hours=1),
            START + timedelta(days=1),
            START + timedelta(days=2),
        ),
    )
    # Date contract rejects unsorted duplicate date aliases rather than guessing.
    with pytest.raises(ValueError, match="CALENDAR"):
        compare_series([a, b], START, END)


@pytest.mark.parametrize("values", [[10, 10, 10], [10, 11, 12], [10, 9, 8]])
def test_drawdown_flat_rising_and_falling_paths(values):
    r = compare_series([series("a", values), series("b", values)], START, END)
    assert Decimal(r["series"][0]["maximum_drawdown_percent"]) == (
        Decimal(20) if values[-1] == 8 else Decimal(0)
    )


def test_provisional_never_silently_replaces_strict_compatibility():
    a = series("a", [10, 11, 12], basis="PROVIDER_ADJUSTED")
    b = series("b", [20, 22, 24], basis="PROVIDER_ADJUSTED")
    assert (
        compare_series([a, b], START, END)["unavailable_reason"]
        == "ADJUSTMENT_COMPATIBILITY_UNVERIFIED"
    )
    r = compare_series([a, b], START, END, provisional_adjustment=True)
    assert (
        r["status"] == "AVAILABLE"
        and r["qualification_status"] == "PROVISIONAL_PROVIDER_AS_DELIVERED"
    )
    a = replace(a, adjustment_definition_ref="different-definition-a")
    b = replace(b, adjustment_definition_ref="different-definition-b")
    assert (
        compare_series([a, b], START, END, provisional_adjustment=True)["status"] == "UNAVAILABLE"
    )


@pytest.mark.parametrize("provisional", [False, True])
def test_known_discontinuity_cannot_be_overridden(provisional):
    a = replace(
        series("a", [10, 11, 12], basis="PROVIDER_ADJUSTED"),
        break_dates=(START + timedelta(days=1),),
    )
    b = series("b", [20, 22, 24], basis="PROVIDER_ADJUSTED")
    assert (
        compare_series([a, b], START, END, provisional_adjustment=provisional)["unavailable_reason"]
        == "PRICE_DISCONTINUITY_UNRESOLVED"
    )


@pytest.mark.parametrize("bad", ["0", "-1", "NaN", "Infinity"])
def test_invalid_prices_never_generate_metrics(bad):
    with pytest.raises(ValueError):
        compare_series([series("a", [1, bad, 2]), series("b", [1, 2, 3])], START, END)


def test_near_zero_prices_use_decimal_and_ignore_global_context():
    a = series("a", ["0.0000000001", "0.0000000002", "0.0000000001"])
    old = getcontext().copy()
    try:
        getcontext().prec = 5
        getcontext().rounding = ROUND_DOWN
        r = compare_series([a, replace(a, key="b")], START, END)
        assert r["series"][0]["maximum_drawdown_percent"] == "50.000000000000"
    finally:
        getcontext().prec = old.prec
        getcontext().rounding = old.rounding


@pytest.mark.parametrize("model_price", ["100", "110", None])
def test_forecast_display_summary_exact_and_volatility_separate(model_price):
    r = SimpleNamespace(
        predicted_price=Decimal(model_price) if model_price else None,
        last_observed_close=Decimal("100"),
    )
    a, p = display_changes(r)
    if model_price is None:
        assert a is p is None
    else:
        assert a == p == Decimal(model_price) - 100


def test_same_dhan_source_opt_in_api_never_retrieves_or_persists(monkeypatch):
    app, service, calls, _ = setup()
    p, data, _ = collected()
    app.state.transient_research.install(
        data,
        p,
        names={x.symbol: "SYNTHETIC TEST ONLY" for x in service.provider.listings()},
        data_class="SYNTHETIC_TEST",
    )
    store = app.state.transient_research

    def fake_db():
        yield SimpleNamespace(info={"transient_research": store.snapshot()})

    app.dependency_overrides[get_db] = fake_db
    src = store.sources()[0]
    src.profile.pop("adjustment_definition_ref", None)
    instruments = store.listings()
    body = {
        "series": [
            {
                "instrument_id": str(i.id),
                "source_id": str(src.id),
                "price_basis": "PROVIDER_ADJUSTED",
            }
            for i in [instruments[0], instruments[1]]
        ],
        "start": str(p.start),
        "end": str(p.end),
    }
    original = export_cache(app)
    with TestClient(app, headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}) as client:
        strict = client.post("/api/v1/comparisons", json=body)
        assert (
            strict.status_code == 422
            and strict.json()["error"]["code"] == "ADJUSTMENT_COMPATIBILITY_UNVERIFIED"
        )
        assert (
            client.post(
                "/api/v1/comparisons",
                json={**body, "qualification_mode": "PROVISIONAL_AS_DELIVERED"},
            ).status_code
            == 422
        )
        response = client.post(
            "/api/v1/comparisons",
            json={
                **body,
                "qualification_mode": "PROVISIONAL_AS_DELIVERED",
                "acknowledge_source_limitations": True,
            },
        )
        assert response.status_code == 200
        result = response.json()["data"]
        assert result["qualification_status"] == "PROVISIONAL_PROVIDER_AS_DELIVERED"
        assert "ADJUSTMENT_COMPATIBILITY_UNVERIFIED" in result["limitations"]
    assert not calls and export_cache(app) == original
    assert (
        src.qualification == "TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED"
        and src.permitted_uses["storage"] is False
    )
