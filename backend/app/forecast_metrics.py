"""Independent descriptive score contracts. No probabilistic metric fabrication."""

from datetime import date
from decimal import Decimal, DecimalException
from pydantic import Field, model_validator
from .forecast_contracts import Frozen, Name, Number, Price, ForecastError
from .forecast_baselines import context, derived


METRICS_VERSION = "descriptive-metrics-v2-bias"


class MetricCase(Frozen):
    case_id: Name
    instrument_id: Name
    origin_session: date
    target_session: date
    origin_price: Price
    actual_price: Price
    realized_volatility: Number
    predicted_price: Number | None
    predicted_return: Number | None
    predicted_volatility: Number | None

    @model_validator(mode="after")
    def coherent(self):
        if self.target_session <= self.origin_session or self.realized_volatility < 0:
            raise ValueError("INVALID_METRIC_TARGET")
        if (self.predicted_price is None) != (self.predicted_return is None):
            raise ValueError("INCOMPLETE_POINT_PREDICTION")
        if self.predicted_price is not None and self.predicted_price <= 0:
            raise ValueError("INVALID_PREDICTED_PRICE")
        if self.predicted_volatility is not None and self.predicted_volatility < 0:
            raise ValueError("INVALID_VOLATILITY")
        return self

    @property
    def key(self):
        return self.instrument_id, self.origin_session, self.target_session


class DirectionCell(Frozen):
    predicted: int = Field(strict=True, ge=-1, le=1)
    actual: int = Field(strict=True, ge=-1, le=1)
    count: int = Field(strict=True, ge=0)


class MetricSummary(Frozen):
    price_samples: int
    volatility_samples: int
    price_mae: Number | None
    price_bias: Number | None = None
    return_bias: Number | None = None
    price_rmse: Number | None
    return_mae: Number | None
    directional_hit_rate: Number | None
    direction_counts: tuple[DirectionCell, ...]
    zero_prediction_count: int
    zero_outcome_count: int
    volatility_proxy_mae: Number | None
    volatility_proxy_rmse: Number | None
    prediction_interval_coverage: None = None
    crps: None = None
    calibration_error: None = None
    unsupported: tuple[str, ...]


class BenchmarkComparison(Frozen):
    benchmark: Name = "B01"
    paired_samples: int
    price_mae_reduction: Number | None
    price_mae_relative_improvement: Number | None
    price_rmse_relative_improvement: Number | None
    return_mae_relative_improvement: Number | None
    unavailable_reason: str | None


def unique(cases):
    if (
        len(cases) > 200
        or len({c.key for c in cases}) != len(cases)
        or len({c.case_id for c in cases}) != len(cases)
    ):
        raise ForecastError("DUPLICATE_OR_EXCESS_METRIC_CASES")


def mean(values):
    return sum(values, Decimal(0)) / len(values)


def sign(value):
    return int(value > 0) - int(value < 0)


def score_cases(cases):
    cases = tuple(cases)
    unique(cases)
    prices = tuple(c for c in cases if c.predicted_price is not None)
    vols = tuple(c for c in cases if c.predicted_volatility is not None)
    counts = {(p, a): 0 for p in (-1, 0, 1) for a in (-1, 0, 1)}
    try:
        with context():
            price_errors = tuple(c.predicted_price - c.actual_price for c in prices)
            return_errors = tuple(
                c.predicted_return - (c.actual_price / c.origin_price - 1) for c in prices
            )
            for c in prices:
                counts[sign(c.predicted_return), sign(c.actual_price / c.origin_price - 1)] += 1
            vol_errors = tuple(c.predicted_volatility - c.realized_volatility for c in vols)
            return MetricSummary(
                price_bias=derived(mean(price_errors)) if prices else None,
                return_bias=derived(mean(return_errors)) if prices else None,
                price_samples=len(prices),
                volatility_samples=len(vols),
                price_mae=derived(mean(tuple(abs(x) for x in price_errors))) if prices else None,
                price_rmse=derived(mean(tuple(x * x for x in price_errors)).sqrt())
                if prices
                else None,
                return_mae=derived(mean(tuple(abs(x) for x in return_errors))) if prices else None,
                directional_hit_rate=derived(
                    Decimal(sum(counts[x, x] for x in (-1, 0, 1))) / len(prices)
                )
                if prices
                else None,
                direction_counts=tuple(
                    DirectionCell(predicted=p, actual=a, count=n) for (p, a), n in counts.items()
                ),
                zero_prediction_count=sum(n for (p, a), n in counts.items() if p == 0),
                zero_outcome_count=sum(n for (p, a), n in counts.items() if a == 0),
                volatility_proxy_mae=derived(mean(tuple(abs(x) for x in vol_errors)))
                if vols
                else None,
                volatility_proxy_rmse=derived(mean(tuple(x * x for x in vol_errors)).sqrt())
                if vols
                else None,
                unsupported=("prediction_interval_coverage", "CRPS", "calibration_error")
                + (() if prices else ("price_metrics", "directional_hit_rate"))
                + (() if vols else ("volatility_metrics",)),
            )
    except DecimalException:
        raise ForecastError("NUMERIC_UNSUPPORTED") from None


def compare_to_b01(candidate, benchmark):
    candidate, benchmark = tuple(candidate), tuple(benchmark)
    unique(candidate)
    unique(benchmark)
    a, b = (
        {c.key: c for c in candidate if c.predicted_price is not None},
        {c.key: c for c in benchmark if c.predicted_price is not None},
    )
    keys = sorted(a.keys() & b.keys())
    if not keys:
        return BenchmarkComparison(
            paired_samples=0,
            price_mae_reduction=None,
            price_mae_relative_improvement=None,
            price_rmse_relative_improvement=None,
            return_mae_relative_improvement=None,
            unavailable_reason="NO_COMMON_SUPPORTED_POINT_TARGETS",
        )
    if any(
        (a[k].origin_price, a[k].actual_price) != (b[k].origin_price, b[k].actual_price)
        for k in keys
    ):
        raise ForecastError("INCOMPATIBLE_BENCHMARK_TARGETS")
    # Benchmark identity is supplied by the evaluator, but enforce its no-change contract too.
    if any(b[k].predicted_price != b[k].origin_price or b[k].predicted_return != 0 for k in keys):
        raise ForecastError("INVALID_B01_BENCHMARK")
    try:
        with context():
            # Use raw losses to avoid relative scores based on quantized near-zero denominators.
            ae = tuple(a[k].predicted_price - a[k].actual_price for k in keys)
            be = tuple(b[k].predicted_price - b[k].actual_price for k in keys)
            ar = tuple(
                a[k].predicted_return - (a[k].actual_price / a[k].origin_price - 1) for k in keys
            )
            br = tuple(
                b[k].predicted_return - (b[k].actual_price / b[k].origin_price - 1) for k in keys
            )
            ma, mb = mean(tuple(abs(x) for x in ae)), mean(tuple(abs(x) for x in be))
            ra, rb = mean(tuple(x * x for x in ae)).sqrt(), mean(tuple(x * x for x in be)).sqrt()
            ta, tb = mean(tuple(abs(x) for x in ar)), mean(tuple(abs(x) for x in br))
            return BenchmarkComparison(
                paired_samples=len(keys),
                price_mae_reduction=derived(mb - ma),
                price_mae_relative_improvement=derived(1 - ma / mb) if mb else None,
                price_rmse_relative_improvement=derived(1 - ra / rb) if rb else None,
                return_mae_relative_improvement=derived(1 - ta / tb) if tb else None,
                unavailable_reason="ZERO_BENCHMARK_LOSS" if not mb else None,
            )
    except DecimalException:
        raise ForecastError("NUMERIC_UNSUPPORTED") from None
