"""Model-independent, immutable transient performance contracts; no I/O."""

from datetime import date
from typing import Literal
from pydantic import Field, model_validator
from .forecast_contracts import Frozen, Name, Number, Stamp, Instrument, Settings
from .forecast_metrics import MetricSummary

Mode = Literal["STRICT_POINT_IN_TIME", "CONDITIONAL_HISTORICAL_REPLAY", "SYNTHETIC"]
Count = int


class EvaluationWindow(Frozen):
    start: date
    end: date

    @model_validator(mode="after")
    def ordered(self):
        if self.start > self.end:
            raise ValueError("INVALID_PERFORMANCE_WINDOW")
        return self


class SampleEvidence(Frozen):
    requested_origins: int = Field(strict=True, ge=0, le=200)
    eligible_origins: int = Field(strict=True, ge=0, le=200)
    scored_origins: int = Field(strict=True, ge=0, le=200)
    unmatched_origins: int = Field(strict=True, ge=0, le=200)
    excluded_origins: int = Field(strict=True, ge=0, le=200)
    pending_origins: int = Field(strict=True, ge=0, le=200)
    unavailable_outcomes: int = Field(strict=True, ge=0, le=200)
    overlapping_pairs: int = Field(strict=True, ge=0)
    disjoint_windows: int = Field(strict=True, ge=0, le=200)
    effective_independent_count: None = None
    independence_status: Literal["NOT_ESTIMATED"] = "NOT_ESTIMATED"

    @model_validator(mode="after")
    def coherent(self):
        if (
            self.scored_origins + self.unmatched_origins != self.eligible_origins
            or self.disjoint_windows > self.scored_origins
            or self.eligible_origins
            + self.excluded_origins
            + self.pending_origins
            + self.unavailable_outcomes
            != self.requested_origins
        ):
            raise ValueError("INCOHERENT_SAMPLE_COUNTS")
        return self


class PerformanceResult(Frozen):
    schema_version: Literal["forecast-performance-v1"] = "forecast-performance-v1"
    result_id: Name
    experiment_id: Name
    model_id: Name
    model_version: Name
    configuration: Settings
    instrument: Instrument
    horizon: int = Field(strict=True, ge=1, le=120)
    evaluation_mode: Mode
    dataset_fingerprint: Name
    basis: Name
    evaluation_window: EvaluationWindow
    sample_basis: Literal["COMMON_B01_B02", "MODEL_ELIGIBLE_ONLY"]
    origin_set_fingerprint: Name
    metric_kind: Literal["POINT_PRICE_RETURN", "VOLATILITY_PROXY"]
    metrics: MetricSummary
    samples: SampleEvidence
    qualification_status: Name
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    assessment_cutoff: Stamp
    computed_at: Stamp
    retention: Literal["PROCESS_MEMORY_ONLY"] = "PROCESS_MEMORY_ONLY"

    @model_validator(mode="after")
    def coherent(self):
        if self.computed_at < self.assessment_cutoff:
            raise ValueError("COMPUTATION_BEFORE_ASSESSMENT")
        if self.metric_kind == "VOLATILITY_PROXY" and (
            self.metrics.price_samples or self.metrics.directional_hit_rate is not None
        ):
            raise ValueError("VOLATILITY_NOT_DIRECTIONAL")
        n = (
            self.metrics.price_samples
            if self.metric_kind == "POINT_PRICE_RETURN"
            else self.metrics.volatility_samples
        )
        if n != self.samples.scored_origins:
            raise ValueError("METRIC_SAMPLE_COUNT_MISMATCH")
        return self


class ErrorPoint(Frozen):
    forecast_id: Name
    model_id: Name
    origin: date
    target: date
    outcome_available_at: Stamp
    unit: Literal["PRICE", "VOLATILITY_PROXY_FRACTION"]
    signed_error: Number
    absolute_error: Number
    percentage_error: Number | None
    return_error: Number | None
    normalization_limits: tuple[str, ...]


class RollingError(Frozen):
    model_id: Name
    first_origin: date
    last_origin: date
    sample_count: int = Field(strict=True, ge=1, le=30)
    requested_window: int = Field(strict=True, ge=2, le=30)
    partial_window: bool
    outcome_known_at: Stamp
    mae: Number
    rmse: Number
    bias: Number
    unit: Literal["PRICE", "VOLATILITY_PROXY_FRACTION"]


class DistributionBin(Frozen):
    label: Name
    count: int = Field(strict=True, ge=0, le=200)


class ErrorDistribution(Frozen):
    model_id: Name
    unit: Literal["RETURN_ERROR_FRACTION", "VOLATILITY_PROXY_FRACTION"]
    sample_count: int = Field(strict=True, ge=0, le=200)
    excluded_count: int = Field(strict=True, ge=0, le=200)
    bins: tuple[DistributionBin, ...]
    p10: Number | None
    median: Number | None
    p90: Number | None
    method: Literal["FIXED_BINS_NEAREST_RANK_RAW_DECIMAL_V1"] = (
        "FIXED_BINS_NEAREST_RANK_RAW_DECIMAL_V1"
    )

    @model_validator(mode="after")
    def counts(self):
        if sum(b.count for b in self.bins) != self.sample_count:
            raise ValueError("INVALID_DISTRIBUTION_COUNTS")
        if (self.sample_count == 0) != (self.median is None):
            raise ValueError("INVALID_DISTRIBUTION_QUANTILES")
        return self


class RegimeEvidence(Frozen):
    rule_version: Literal["fixed-21-close-v1"] = "fixed-21-close-v1"
    origin: date
    first_session: date | None
    input_count: int = Field(strict=True, ge=0, le=21)
    context_fingerprint: Name
    latest_input_available_at: Stamp
    trend: Literal["TRENDING", "SIDEWAYS", "UNAVAILABLE"]
    volatility: Literal["HIGH", "LOW", "UNAVAILABLE"]
    efficiency: Number | None
    trailing_return: Number | None
    session_sigma: Number | None
    reason: Name | None


class RegimeSummary(Frozen):
    model_id: Name
    axis: Literal["TREND", "VOLATILITY"]
    label: Literal["TRENDING", "SIDEWAYS", "HIGH", "LOW", "UNAVAILABLE"]
    metrics: MetricSummary
    scored_origins: int = Field(strict=True, ge=0, le=200)
    overlapping_pairs: int = Field(strict=True, ge=0)
    disjoint_windows: int = Field(strict=True, ge=0, le=200)
    limitations: tuple[str, ...]


class CommonComparison(Frozen):
    model_ids: tuple[str, ...]
    common_origins: int = Field(strict=True, ge=0, le=200)
    origin_set_fingerprint: Name | None
    b02_minus_b01_mae: Number | None
    interpretation: Literal["DESCRIPTIVE_PAIRED_LOSS_DIFFERENCE_NO_SUPERIORITY_CLAIM"] = (
        "DESCRIPTIVE_PAIRED_LOSS_DIFFERENCE_NO_SUPERIORITY_CLAIM"
    )
    reason: Name | None


class PerformanceAnalysis(Frozen):
    schema_version: Literal["forecast-performance-analysis-v1"] = "forecast-performance-analysis-v1"
    cards: tuple[PerformanceResult, ...] = Field(min_length=1, max_length=3)
    comparison: CommonComparison
    errors: tuple[ErrorPoint, ...] = Field(max_length=600)
    rolling: tuple[RollingError, ...] = Field(max_length=600)
    distributions: tuple[ErrorDistribution, ...] = Field(max_length=3)
    regimes: tuple[RegimeSummary, ...] = Field(max_length=18)
    regime_rule_version: Name | None
    rolling_window: int = Field(strict=True, ge=2, le=30)
    warnings: tuple[str, ...]

    @model_validator(mode="after")
    def no_mixing(self):
        a = self.cards[0]
        keys = (
            "instrument",
            "horizon",
            "evaluation_mode",
            "dataset_fingerprint",
            "basis",
            "evaluation_window",
            "experiment_id",
            "assessment_cutoff",
        )
        if any(any(getattr(a, k) != getattr(b, k) for k in keys) for b in self.cards[1:]):
            raise ValueError("INCOMPATIBLE_PERFORMANCE_RESULTS")
        if len({c.model_id for c in self.cards}) != len(self.cards):
            raise ValueError("DUPLICATE_PERFORMANCE_MODEL")
        return self
