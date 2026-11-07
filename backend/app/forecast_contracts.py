"""Package 3 immutable, synthetic-only contracts. No provider, DB or environment access."""

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Annotated, Literal, Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    AfterValidator,
    BeforeValidator,
    StrictStr,
    StrictInt,
    StrictBool,
    PlainSerializer,
    model_validator,
)

CONTRACT_VERSION = "forecast-contract-v2"
NUMERIC_VERSION = "decimal34-half-even-wire12-v1"
HORIZONS = (1, 5, 20, 60, 120)


class ForecastError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class Frozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, hide_input_in_errors=True)


def utc(value):
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return value.astimezone(timezone.utc)


Stamp = Annotated[datetime, AfterValidator(utc)]
Name = Annotated[str, Field(min_length=1, max_length=128)]


def decimal_input(value):
    if not isinstance(value, (str, Decimal)):
        raise ValueError("DECIMAL_STRING_OR_DECIMAL_REQUIRED")
    if isinstance(value, str) and len(value) > 128:
        raise ValueError("DECIMAL_INPUT_TOO_LONG")
    try:
        d = Decimal(value)
    except InvalidOperation:
        raise ValueError("INVALID_DECIMAL") from None
    if not d.is_finite() or len(d.as_tuple().digits) > 34:
        raise ValueError("FINITE_DECIMAL34_REQUIRED")
    if not -96 <= d.as_tuple().exponent <= 96 or (d and not -96 <= d.adjusted() <= 96):
        raise ValueError("NUMERIC_EXPONENT_UNSUPPORTED")
    return d


Price = Annotated[
    Decimal,
    BeforeValidator(decimal_input),
    Field(ge=Decimal("1e-12"), le=Decimal("1e12")),
    PlainSerializer(lambda v: format(v, "f"), return_type=str, when_used="json"),
]
Number = Annotated[
    Decimal,
    BeforeValidator(decimal_input),
    PlainSerializer(lambda v: format(v, "f"), return_type=str, when_used="json"),
]


def canonical(value):
    if isinstance(value, BaseModel):
        return canonical(value.model_dump())
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ForecastError("INVALID_NUMERIC_VALUE")
        text = format(value, "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
    if isinstance(value, datetime):
        return utc(value).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [canonical(v) for v in value]
    return value


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(
            canonical(value), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


class Instrument(Frozen):
    instrument_id: Name
    symbol: Annotated[str, Field(min_length=1, max_length=32, pattern=r"^[A-Z0-9_.-]+$")]
    exchange: Name
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
    isin: str | None = Field(default=None, max_length=16)


class CalendarSession(Frozen):
    session_date: date
    close_at: Stamp


class TradingCalendar(Frozen):
    calendar_id: Name
    version: Name
    timezone: Name
    known_at: Stamp
    coverage_start: date
    coverage_end: date
    sessions: tuple[CalendarSession, ...] = Field(min_length=1, max_length=5000)

    @model_validator(mode="after")
    def coherent(self):
        try:
            zone = ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError:
            raise ValueError("UNKNOWN_TIMEZONE") from None
        days = [s.session_date for s in self.sessions]
        closes = [s.close_at for s in self.sessions]
        if days != sorted(set(days)) or closes != sorted(set(closes)):
            raise ValueError("CALENDAR_ORDER_OR_DUPLICATES")
        if self.coverage_start > days[0] or self.coverage_end < days[-1]:
            raise ValueError("CALENDAR_COVERAGE")
        if any(s.close_at.astimezone(zone).date() != s.session_date for s in self.sessions):
            raise ValueError("SESSION_TIMEZONE_DATE_MISMATCH")
        return self


class Provenance(Frozen):
    source_id: Name
    source_version: Name
    dataset_label: Name
    evidence_ref: Name
    known_at: Stamp
    data_class: Literal["SYNTHETIC_TEST"] = "SYNTHETIC_TEST"


class ForecastObservation(Frozen):
    session_date: date
    observed_at: Stamp
    available_at: Stamp
    open: Price
    high: Price
    low: Price
    close: Price
    volume: int = Field(strict=True, ge=0, le=9223372036854775807)
    completed: bool = Field(strict=True)
    quality: Literal["QUALIFIED_SYNTHETIC", "DEGRADED", "UNKNOWN"]
    provenance_ref: Name

    @model_validator(mode="after")
    def coherent(self):
        if not self.low <= self.open <= self.high or not self.low <= self.close <= self.high:
            raise ValueError("INCONSISTENT_OHLC")
        if self.available_at < self.observed_at:
            raise ValueError("AVAILABILITY_BEFORE_OBSERVATION")
        return self


class CorporateAction(Frozen):
    effective_session: date
    available_at: Stamp
    kind: Literal["SPLIT", "DISTRIBUTION", "OTHER"]
    evidence_ref: Name


class ForecastDataset(Frozen):
    schema_version: Literal["forecast-input-v1"] = "forecast-input-v1"
    instrument: Instrument
    timeframe: Literal["1d"] = "1d"
    calendar: TradingCalendar
    provenance: Provenance
    basis: Literal["RAW_CLOSE", "PIT_ADJUSTED_CLOSE"]
    adjustment_policy_id: Name
    adjustment_vintage_at: Stamp | None = None
    observations: tuple[ForecastObservation, ...] = Field(max_length=5000)
    corporate_actions: tuple[CorporateAction, ...] = Field(default=(), max_length=500)

    @model_validator(mode="after")
    def coherent(self):
        days = [r.session_date for r in self.observations]
        times = [r.observed_at for r in self.observations]
        if days != sorted(set(days)) or times != sorted(set(times)):
            raise ValueError("OBSERVATION_ORDER_OR_DUPLICATES")
        sessions = {s.session_date: s for s in self.calendar.sessions}
        if any(
            r.session_date not in sessions or r.observed_at != sessions[r.session_date].close_at
            for r in self.observations
        ):
            raise ValueError("OBSERVATION_SESSION_MISMATCH")
        if self.basis == "PIT_ADJUSTED_CLOSE" and (
            self.adjustment_vintage_at is None or self.adjustment_policy_id == "RAW_NO_ACTIONS"
        ):
            raise ValueError("ADJUSTMENT_VINTAGE_REQUIRED")
        if self.basis == "RAW_CLOSE" and (
            self.adjustment_vintage_at is not None or self.adjustment_policy_id != "RAW_NO_ACTIONS"
        ):
            raise ValueError("RAW_BASIS_POLICY_MISMATCH")
        if self.adjustment_vintage_at and any(
            r.available_at < self.adjustment_vintage_at for r in self.observations
        ):
            raise ValueError("ADJUSTED_VALUE_BEFORE_VINTAGE")
        if any(a.effective_session not in sessions for a in self.corporate_actions):
            raise ValueError("ACTION_OUTSIDE_CALENDAR")
        return self


class QualityRequirements(Frozen):
    require_complete: bool = Field(default=True, strict=True)
    require_contiguous: bool = Field(default=True, strict=True)
    quality: Literal["QUALIFIED_SYNTHETIC"] = "QUALIFIED_SYNTHETIC"
    max_publication_delay_seconds: int | None = Field(default=None, strict=True, ge=0, le=31536000)

    @model_validator(mode="after")
    def no_relaxation(self):
        if not self.require_complete or not self.require_contiguous:
            raise ValueError("QUALITY_RELAXATION_UNSUPPORTED")
        return self


class Setting(Frozen):
    name: Name
    value: Annotated[StrictStr, Field(max_length=256)] | StrictInt | StrictBool | None


Settings = tuple[Setting, ...]


def settings_valid(values):
    names = [s.name for s in values]
    if len(names) > 16 or len(set(names)) != len(names):
        raise ValueError("DUPLICATE_OR_EXCESS_SETTINGS")
    return tuple(sorted(values, key=lambda s: s.name))


class ForecastRequest(Frozen):
    instrument: Instrument
    timeframe: Literal["1d"] = "1d"
    origin_session: date
    horizon: int = Field(strict=True)
    lookback: int = Field(strict=True, ge=1, le=1000)
    model_id: Name
    configuration: Settings = ()
    cutoff: Stamp
    quality: QualityRequirements = Field(default_factory=QualityRequirements)

    @model_validator(mode="after")
    def coherent(self):
        if self.horizon not in HORIZONS:
            raise ValueError("UNSUPPORTED_HORIZON")
        object.__setattr__(self, "configuration", settings_valid(self.configuration))
        return self


class ForecastSnapshot(Frozen):
    instrument: Instrument
    timeframe: Literal["1d"] = "1d"
    origin_session: date
    target_session: CalendarSession
    horizon: int = Field(strict=True)
    lookback: int = Field(strict=True, ge=1, le=1000)
    cutoff: Stamp
    calendar_id: Name
    calendar_version: Name
    calendar_fingerprint: Name
    context_sessions: tuple[CalendarSession, ...]
    observations: tuple[ForecastObservation, ...]
    provenance: Provenance
    basis: Literal["RAW_CLOSE", "PIT_ADJUSTED_CLOSE"]
    adjustment_policy_id: Name
    adjustment_vintage_at: Stamp | None
    quality: QualityRequirements

    @model_validator(mode="after")
    def coherent(self):
        if (
            self.horizon not in HORIZONS
            or len(self.observations) != self.lookback
            or len(self.context_sessions) != self.lookback
        ):
            raise ValueError("INVALID_CONTEXT_LENGTH")
        days = [r.session_date for r in self.observations]
        if not days or days[-1] != self.origin_session or days != sorted(set(days)):
            raise ValueError("INVALID_CONTEXT_ORIGIN")
        if days != [s.session_date for s in self.context_sessions]:
            raise ValueError("NONCONTIGUOUS_CONTEXT")
        if self.provenance.known_at > self.cutoff or (
            self.adjustment_vintage_at and self.adjustment_vintage_at > self.cutoff
        ):
            raise ValueError("METADATA_NOT_AVAILABLE")
        if self.target_session.close_at <= self.cutoff:
            raise ValueError("TARGET_NOT_FUTURE")
        for r, s in zip(self.observations, self.context_sessions):
            if (
                r.observed_at != s.close_at
                or r.available_at > self.cutoff
                or r.observed_at > self.cutoff
            ):
                raise ValueError("UNAVAILABLE_CONTEXT")
            if not r.completed or r.quality != self.quality.quality:
                raise ValueError("INELIGIBLE_CONTEXT")
            lag = self.quality.max_publication_delay_seconds
            if lag is not None and (r.available_at - r.observed_at).total_seconds() > lag:
                raise ValueError("PUBLICATION_DELAY_EXCEEDED")
        return self

    @property
    def fingerprint(self):
        return fingerprint({"contract": CONTRACT_VERSION, "snapshot": self})


class ModelDescriptor(Frozen):
    model_id: Name
    version: Name
    min_closes: int = Field(strict=True, ge=1)
    capabilities: tuple[Literal["POINT_PRICE", "POINT_RETURN", "VOLATILITY"], ...]
    supported_horizons: tuple[int, ...] = HORIZONS
    lifecycle: Literal["OFFLINE_SYNTHETIC_RESEARCH_ONLY"] = "OFFLINE_SYNTHETIC_RESEARCH_ONLY"


class PredictionInterval(Frozen):
    lower: Number
    upper: Number
    nominal_coverage: Number

    @model_validator(mode="after")
    def coherent(self):
        if self.lower > self.upper or not 0 < self.nominal_coverage < 1:
            raise ValueError("INVALID_INTERVAL")
        return self


class ForecastResult(Frozen):
    forecast_id: Name
    contract_version: Literal["forecast-contract-v2"] = CONTRACT_VERSION
    model: ModelDescriptor
    instrument: Instrument
    horizon: int = Field(strict=True)
    origin_session: date
    target_session: date
    created_at: Stamp
    cutoff: Stamp
    dataset_fingerprint: Name
    configuration: Settings
    basis: Literal["RAW_CLOSE", "PIT_ADJUSTED_CLOSE"]
    provenance: Provenance
    data_quality: Literal["QUALIFIED_SYNTHETIC"] = "QUALIFIED_SYNTHETIC"
    observations_validated: int = Field(strict=True, ge=1, le=1000)
    effective_closes_used: int = Field(strict=True, ge=1, le=1000)
    return_observations_used: int = Field(strict=True, ge=0, le=999)
    last_observed_close: Price
    last_observation_at: Stamp | None
    last_availability_at: Stamp
    last_session_close_proxy: Stamp
    predicted_price: Number | None = None
    predicted_return: Number | None = None
    session_volatility: Number | None = None
    horizon_volatility: Number | None = None
    annualized_volatility: Number | None = None
    prediction_intervals: tuple[PredictionInterval, ...] | None = None
    probability_positive: Number | None = None
    calibration_status: Literal["NOT_SUPPORTED"] = "NOT_SUPPORTED"
    unsupported_fields: tuple[str, ...]
    warnings: tuple[str, ...]
    numeric_version: Literal["decimal34-half-even-wire12-v1"] = NUMERIC_VERSION

    @model_validator(mode="after")
    def coherent(self):
        if (
            self.effective_closes_used > self.observations_validated
            or self.return_observations_used > self.effective_closes_used - 1
        ):
            raise ValueError("INVALID_EFFECTIVE_OBSERVATION_COUNTS")
        caps = self.model.capabilities
        if self.horizon not in self.model.supported_horizons or self.created_at < self.cutoff:
            raise ValueError("INVALID_FORECAST_TIME_OR_HORIZON")
        if self.prediction_intervals is not None or self.probability_positive is not None:
            raise ValueError("PROBABILISTIC_OUTPUT_UNSUPPORTED")
        if (self.predicted_price is not None) != ("POINT_PRICE" in caps) or (
            self.predicted_return is not None
        ) != ("POINT_RETURN" in caps):
            raise ValueError("POINT_CAPABILITY_MISMATCH")
        if (self.horizon_volatility is not None) != ("VOLATILITY" in caps) or (
            self.session_volatility is not None
        ) != ("VOLATILITY" in caps):
            raise ValueError("VOLATILITY_CAPABILITY_MISMATCH")
        if self.predicted_price is not None and self.predicted_price <= 0:
            raise ValueError("NONPOSITIVE_PREDICTED_PRICE")
        if any(
            v is not None and v < 0
            for v in (self.session_volatility, self.horizon_volatility, self.annualized_volatility)
        ):
            raise ValueError("NEGATIVE_VOLATILITY")
        return self


class ForecastModel(Protocol):
    """Future adapter seam only; no external adapter implementation or loader."""

    descriptor: ModelDescriptor

    def predict(
        self, snapshot: ForecastSnapshot, request: ForecastRequest, *, created_at: datetime
    ) -> ForecastResult: ...
