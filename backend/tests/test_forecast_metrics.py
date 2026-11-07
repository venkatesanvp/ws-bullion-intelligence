from datetime import date, timedelta
from decimal import Decimal, localcontext
import pytest
from app.forecast_contracts import ForecastError
from app.forecast_metrics import MetricCase, score_cases, compare_to_b01


def cases():
    out = []
    for i, (actual, pred, ret, vol, rv) in enumerate(
        [("12", "11", ".1", ".3", ".2"), ("8", "10", "0", ".1", ".2"), ("8", "8", "-.2", "0", "0")]
    ):
        origin = date(2024, 1, 1) + timedelta(days=i)
        out.append(
            MetricCase(
                case_id="SYNTH-" + str(i),
                instrument_id="SYNTH",
                origin_session=origin,
                target_session=origin + timedelta(days=5),
                origin_price=Decimal(10),
                actual_price=Decimal(actual),
                predicted_price=Decimal(pred),
                predicted_return=Decimal(ret),
                predicted_volatility=Decimal(vol),
                realized_volatility=Decimal(rv),
            )
        )
    return tuple(out)


def benchmark(rows):
    return tuple(
        MetricCase.model_validate(
            {
                **c.model_dump(),
                "case_id": "B01-" + c.case_id,
                "predicted_price": c.origin_price,
                "predicted_return": Decimal(0),
                "predicted_volatility": None,
            }
        )
        for c in rows
    )


def test_independent_hand_calculated_metrics_and_three_way_direction():
    r = score_cases(cases())
    assert r.price_samples == r.volatility_samples == 3
    assert r.price_mae == 1 and r.return_mae == Decimal(".1")
    assert r.price_bias == Decimal(".333333333333") and r.return_bias == Decimal(".033333333333")
    assert (
        r.directional_hit_rate == Decimal(".666666666667")
        and r.zero_prediction_count == 1
        and r.zero_outcome_count == 0
    )
    with localcontext() as ctx:
        ctx.prec = 100
        assert r.price_rmse == (Decimal(5) / 3).sqrt().quantize(Decimal("1e-12"))
        assert r.volatility_proxy_mae == (Decimal(2) / 30).quantize(Decimal("1e-12"))
        assert r.volatility_proxy_rmse == (Decimal(2) / 300).sqrt().quantize(Decimal("1e-12"))
    assert sum(x.count for x in r.direction_counts) == 3
    assert r.prediction_interval_coverage is r.crps is r.calibration_error is None


def test_benchmark_relative_improvement_matches_same_target_raw_losses():
    a = cases()
    r = compare_to_b01(a, benchmark(a))
    assert r.paired_samples == 3
    assert (
        r.price_mae_reduction == 1
        and r.price_mae_relative_improvement == Decimal(".5")
        and r.return_mae_relative_improvement == Decimal(".5")
    )
    with localcontext() as ctx:
        ctx.prec = 100
        assert r.price_rmse_relative_improvement == (1 - (Decimal(5) / 3).sqrt() / 2).quantize(
            Decimal("1e-12")
        )
    assert compare_to_b01(a[:1], benchmark(a[1:])).paired_samples == 0


def test_zero_benchmark_denominator_is_unavailable_not_infinite_skill():
    c = cases()[1]
    c = MetricCase.model_validate(
        {
            **c.model_dump(),
            "actual_price": Decimal(10),
            "predicted_price": Decimal(11),
            "predicted_return": Decimal(".1"),
        }
    )
    r = compare_to_b01((c,), benchmark((c,)))
    assert (
        r.unavailable_reason == "ZERO_BENCHMARK_LOSS"
        and r.price_mae_relative_improvement is None
        and r.price_mae_reduction == -1
    )


def test_empty_and_unsupported_metrics_are_not_zero_accuracy():
    r = score_cases(())
    assert (
        r.price_samples == r.volatility_samples == 0
        and r.price_mae is r.directional_hit_rate is r.volatility_proxy_mae is None
    )
    c = cases()[0]
    v = MetricCase.model_validate(
        {**c.model_dump(), "predicted_price": None, "predicted_return": None}
    )
    r = score_cases((v,))
    assert r.volatility_samples == 1 and r.price_mae is None
    assert (
        compare_to_b01((v,), benchmark((c,))).unavailable_reason
        == "NO_COMMON_SUPPORTED_POINT_TARGETS"
    )


def test_incompatible_targets_and_duplicate_scoring_rejected():
    a = cases()
    b = benchmark(a)
    bad = MetricCase.model_validate({**b[0].model_dump(), "actual_price": Decimal(13)})
    with pytest.raises(ForecastError, match="INCOMPATIBLE_BENCHMARK_TARGETS"):
        compare_to_b01(a, (bad,) + b[1:])
    with pytest.raises(ForecastError, match="DUPLICATE"):
        score_cases(a + a)
    with pytest.raises(ForecastError, match="INVALID_B01"):
        compare_to_b01(a, a)


def test_zero_outcome_is_its_own_direction_class():
    c = cases()[1]
    c = MetricCase.model_validate(
        {
            **c.model_dump(),
            "actual_price": Decimal(10),
            "predicted_price": Decimal(10),
            "predicted_return": Decimal(0),
        }
    )
    r = score_cases((c,))
    assert r.zero_outcome_count == r.zero_prediction_count == 1 and r.directional_hit_rate == 1


@pytest.mark.parametrize("bad", [Decimal("1e1000000"), Decimal("0e-1000000"), "1" * 129])
def test_extreme_numeric_encodings_rejected_before_serialization(bad):
    from pydantic import ValidationError

    c = cases()[0]
    with pytest.raises(ValidationError):
        MetricCase.model_validate({**c.model_dump(), "predicted_return": bad})
