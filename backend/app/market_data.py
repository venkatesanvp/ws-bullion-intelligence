"""D-14 / CMP-03/04: in-memory provider-neutral daily acquisition contracts.

No ORM/session, networking, persistence, analytics or application startup hooks.
Dates at this boundary are inclusive, matching DC-07; provider translation is internal.
"""

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal, localcontext
from typing import Protocol

from .schemas import CalendarProfile
from .serialization import digest


@dataclass(frozen=True)
class Listing:
    exchange: str
    symbol: str
    isin: str
    metal: str
    currency: str = "INR"


@dataclass(frozen=True)
class DailyRequest:
    listing: Listing
    start: date
    end: date
    calendar: CalendarProfile | None = field(default=None, repr=False, compare=False)

    def validate(self):
        if self.calendar is not None:
            if not isinstance(self.calendar, CalendarProfile):
                raise ValueError("INVALID_CALENDAR")
            CalendarProfile.model_validate(self.calendar.model_dump())
        # Technical request/resource limits, not a provider coverage or financial policy.
        if (
            type(self.start) is not date
            or type(self.end) is not date
            or not date(2000, 1, 1) <= self.start <= self.end < date(2100, 1, 1)
            or (self.end - self.start).days >= 366
        ):
            raise ValueError("INVALID_DATE_RANGE")
        if self.calendar is not None and (
            not isinstance(self.calendar, CalendarProfile)
            or self.calendar.coverage_start > self.start
            or self.calendar.coverage_end < self.end
        ):
            raise ValueError("CALENDAR_COVERAGE_INSUFFICIENT")


@dataclass(frozen=True)
class ValidationSummary:
    observation_count: int = 0
    issues: tuple[str, ...] = ()
    candidate_dates: tuple[date, ...] = ()
    missing_sessions: tuple[date, ...] | None = None
    calendar_assessment: str = "UNASSESSED"
    duplicate_timestamps: int | None = None
    duplicate_session_dates: int | None = None
    timestamp_conversion_failures: int = 0
    numeric_counters: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = ()


@dataclass(frozen=True)
class BatchProvenance:
    provider: str
    contract_version: str
    listing: Listing
    provider_instrument_id: str
    provider_exchange_segment: str
    provider_instrument_type: str
    requested_start: date
    requested_end: date
    provider_end_exclusive: date
    retrieved_at: datetime
    price_basis: str
    adjustment_reference: str
    timestamp_policy: str
    timestamp_evidence_reference: str
    exchange_timezone: str
    calendar_version: str | None
    calendar_evidence_reference: str | None
    validation_status: str
    limitations: tuple[str, ...]
    source_qualification: str = "UNVERIFIED"
    replay_status: str = "UNVERIFIED_FOR_REPLAY"
    timestamp_semantics_verified: bool = False
    adjustment_method_verified: bool = False
    data_class: str = "REAL_MARKET_CANDIDATE"


@dataclass(frozen=True)
class ObservationProvenance:
    batch: BatchProvenance
    source_row: int
    source_timestamp: str = field(repr=False)
    source_timestamp_encoding: str
    event_time_reason: str = "PROVIDER_SESSION_CONVENTION_UNVERIFIED"
    provider_published_at_reason: str = "NOT_SUPPLIED"


@dataclass(frozen=True, repr=False)
class DailyObservation:
    trading_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    provenance: ObservationProvenance
    interval: str = "1d"
    price_basis: str = "PROVIDER_ADJUSTED"
    event_precision: str = "SESSION_DATE"
    event_time: None = None
    provider_published_at: None = None

    def canonical_values(self) -> dict:
        # Exactly the existing CSV candidate keys, without inventing event/publication times.
        return {
            name: getattr(self, name)
            for name in (
                "trading_date",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "interval",
                "price_basis",
                "event_precision",
                "event_time",
                "provider_published_at",
            )
        }

    @property
    def canonical_hash(self) -> str:
        with localcontext() as context:
            context.prec = 34
            values = {
                k: format(v.normalize(), "f") if isinstance(v, Decimal) else v
                for k, v in self.canonical_values().items()
            }
            return digest(values)


@dataclass(frozen=True)
class ProviderFailure:
    code: str
    http_status: int | None = None
    provider_code: str | None = None


@dataclass(frozen=True)
class DailyResult:
    status: str
    request_attempts: int = 0
    http_status: int | None = None
    observations: tuple[DailyObservation, ...] = field(default=(), repr=False)
    provenance: BatchProvenance | None = None
    validation: ValidationSummary = field(default_factory=ValidationSummary)
    failure: ProviderFailure | None = None

    def safe_summary(self) -> dict:
        # Deliberately excludes observations, raw timestamps, prices and volumes.
        return {
            "status": self.status,
            "request_attempts": self.request_attempts,
            "http_status": self.http_status,
            "validation": asdict(self.validation),
            "provenance": asdict(self.provenance) if self.provenance else None,
            "failure": asdict(self.failure) if self.failure else None,
        }


class DailyMarketDataProvider(Protocol):
    identity: str

    def listings(self) -> tuple[Listing, ...]: ...

    def retrieve_daily(
        self, request: DailyRequest, *, request_approved: bool = False
    ) -> DailyResult: ...
