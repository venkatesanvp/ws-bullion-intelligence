from datetime import timedelta
from decimal import Decimal, localcontext, getcontext, ROUND_HALF_EVEN
from fractions import Fraction
import pytest
from pydantic import ValidationError
from app.forecast_contracts import ForecastRequest, ForecastResult, Setting, ForecastError
from app.forecast_baselines import get_model
from app.forecast_dataset import build_snapshot
from .forecast_fixtures import dataset, request
from .test_forecast_dataset import row_change


def wire_fraction(f):
    with localcontext() as ctx:
        ctx.prec = 100
        ctx.rounding = ROUND_HALF_EVEN
        return (Decimal(f.numerator) / Decimal(f.denominator)).quantize(Decimal("1e-12"))


def run(d, model="B02", **kwargs):
    q = request(d, model=model, **kwargs)
    s = build_snapshot(d, q)
    return get_model(model).predict(s, q, created_at=q.cutoff + timedelta(days=1))


@pytest.mark.parametrize("model", ["B01", "B02", "B03"])
@pytest.mark.parametrize("horizon", [1, 5, 20, 60, 120])
def test_constant_prices_all_horizons_without_invented_probabilities(model, horizon):
    result = run(dataset([100] * 10), model, lookback=10, horizon=horizon)
    assert (
        result.calibration_status == "NOT_SUPPORTED"
        and result.prediction_intervals is None
        and result.probability_positive is None
    )
    if model == "B03":
        assert (
            result.predicted_price is None
            and result.predicted_return is None
            and result.session_volatility == result.horizon_volatility == 0
        )
    else:
        assert (
            result.predicted_price == 100
            and result.predicted_return == 0
            and result.horizon_volatility is None
        )


@pytest.mark.parametrize("horizon", [1, 5, 20, 60, 120])
@pytest.mark.parametrize(
    "closes", [[100, 110, 99, Decimal("118.8")], [100, 90, 81, Decimal("72.9")]]
)
def test_drift_matches_exact_rational_arithmetic_compounding(horizon, closes):
    d = dataset(closes)
    r = run(d, lookback=4, horizon=horizon)
    p = [Fraction(str(v)) for v in closes]
    returns = [b / a - 1 for a, b in zip(p, p[1:])]
    mu = sum(returns) / len(returns)
    factor = (1 + mu) ** horizon
    assert r.predicted_price == wire_fraction(p[-1] * factor)
    assert r.predicted_return == wire_fraction(factor - 1)
    assert r.annualized_volatility is None


def test_naive_preserves_last_observed_price_exactly_not_an_estimated_mean():
    price = Decimal("100.1234567890123456789012345678901")
    r = run(dataset([90, 95, price]), "B01", lookback=1)
    assert r.predicted_price == price and r.predicted_return == 0


@pytest.mark.parametrize("horizon", [1, 5, 20, 60, 120])
def test_volatility_sample_variance_and_sqrt_scaling_independent_high_precision(horizon):
    d = dataset([100, 110, 99, Decimal("118.8")])
    r = run(
        d,
        "B03",
        lookback=4,
        horizon=horizon,
        configuration=(Setting(name="annualization_sessions", value=252),),
    )
    # Independent exact returns [1/10,-1/10,1/5], centered sample variance=7/300.
    with localcontext() as ctx:
        ctx.prec = 100
        ctx.rounding = ROUND_HALF_EVEN
        variance = Decimal(7) / 300
        assert r.session_volatility == variance.sqrt().quantize(Decimal("1e-12"))
        assert r.horizon_volatility == (variance * horizon).sqrt().quantize(Decimal("1e-12"))
        assert r.annualized_volatility == (variance * 252).sqrt().quantize(Decimal("1e-12"))
    assert "IID_SQRT_SESSION_SCALING_ASSUMPTION" in r.warnings
    assert r.predicted_price is None and r.predicted_return is None


@pytest.mark.parametrize("model,lookback", [("B01", 1), ("B02", 2), ("B03", 3)])
def test_computational_minimum_is_explicit_and_shorter_history_rejected(model, lookback):
    d = dataset()
    assert run(d, model, lookback=lookback)
    if lookback > 1:
        with pytest.raises(ForecastError, match="INSUFFICIENT_MODEL_HISTORY"):
            run(d, model, lookback=lookback - 1)


@pytest.mark.parametrize(
    "config",
    [
        (Setting(name="return_convention", value="LOG"),),
        (Setting(name="annualization_sessions", value=True),),
        (Setting(name="annualization_sessions", value=0),),
        (Setting(name="unexpected", value="bad"),),
    ],
)
def test_unsupported_model_configurations_rejected(config):
    with pytest.raises(ForecastError):
        run(dataset(), "B03", configuration=config)


def test_annualization_only_for_volatility_and_unknown_model_rejected():
    with pytest.raises(ForecastError, match="INVALID_ANNUALIZATION"):
        run(dataset(), "B02", configuration=(Setting(name="annualization_sessions", value=252),))
    with pytest.raises(ForecastError, match="MODEL_NOT_REGISTERED"):
        get_model("KRONOS")


def test_future_values_cannot_change_forecast_identity_or_output():
    d = dataset()
    q = request(d, index=10)
    s = build_snapshot(d, q)
    m = get_model("B02")
    first = m.predict(s, q, created_at=q.cutoff)
    changed = row_change(
        d, 20, open=Decimal(999), high=Decimal(999), low=Decimal(999), close=Decimal(999)
    )
    replay = m.predict(build_snapshot(changed, q), q, created_at=q.cutoff + timedelta(days=100))
    assert (
        first.forecast_id == replay.forecast_id and first.predicted_price == replay.predicted_price
    )
    assert first.created_at != replay.created_at
    altered = request(d, index=10, lookback=4)
    assert (
        m.predict(build_snapshot(d, altered), altered, created_at=altered.cutoff).forecast_id
        != first.forecast_id
    )


def test_request_snapshot_mismatch_and_unsupported_response_outputs():
    d = dataset()
    q = request(d)
    s = build_snapshot(d, q)
    other = ForecastRequest.model_validate({**q.model_dump(), "horizon": 20})
    with pytest.raises(ForecastError, match="SNAPSHOT_REQUEST_MISMATCH"):
        get_model("B02").predict(s, other, created_at=q.cutoff)
    with pytest.raises(ForecastError, match="EXECUTION_BEFORE_CUTOFF"):
        get_model("B02").predict(s, q, created_at=q.cutoff - timedelta(seconds=1))
    result = run(d)
    with pytest.raises(ValidationError):
        ForecastResult.model_validate(
            {**result.model_dump(), "probability_positive": Decimal("0.5")}
        )
    with pytest.raises(ValidationError):
        ForecastResult.model_validate({**result.model_dump(), "predicted_price": None})
    forged = s.model_copy(update={"observations": d.observations[:3]})
    with pytest.raises(ForecastError):
        get_model("B02").predict(forged, q, created_at=q.cutoff)


@pytest.mark.parametrize("price", [Decimal("1e-12"), Decimal("1e12")])
def test_supported_numeric_extremes_constant_prices(price):
    d = dataset([price] * 5)
    assert run(d, "B01").predicted_price == price
    assert run(d, "B02").predicted_price == price
    assert run(d, "B03").horizon_volatility == 0


@pytest.mark.parametrize(
    "closes", [[Decimal("1e-12"), Decimal("1e12")], [Decimal("2e-12"), Decimal("1e-12")]]
)
def test_unrepresentable_compounding_fails_without_clipping_or_fake_price(closes):
    with pytest.raises(ForecastError, match="NUMERIC_UNSUPPORTED"):
        run(dataset(closes), "B02", lookback=2, horizon=120)


def test_global_decimal_context_is_not_used_or_mutated():
    d = dataset([100, 110, 99, Decimal("118.8")])
    first = run(d, "B03", lookback=4)
    before = getcontext().prec
    try:
        getcontext().prec = 6
        second = run(d, "B03", lookback=4)
        assert first == second and getcontext().prec == 6
    finally:
        getcontext().prec = before


def test_wire_numbers_are_fixed_decimal_strings_not_binary_floats_or_exponents():
    r = run(dataset([100] * 5), "B02")
    wire = r.model_dump(mode="json")
    assert wire["predicted_return"] == "0.000000000000"
    assert wire["predicted_price"] == "100.000000000000"
    assert wire["prediction_intervals"] is None
