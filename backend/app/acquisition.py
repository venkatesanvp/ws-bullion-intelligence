"""D-14 / DC-02..04: bounded provider-neutral history collection, without I/O storage."""

from dataclasses import dataclass, field
from datetime import date, timedelta
import time
from typing import Callable

from pydantic import Field, model_validator
from .market_data import (
    DailyMarketDataProvider,
    DailyObservation,
    DailyRequest,
    DailyResult,
    Listing,
)
from .schemas import CalendarProfile, Strict
from .serialization import digest, plain


class Availability(Strict):
    inception_date: date
    evidence_ref: str = Field(min_length=1, max_length=1000)


class HistoryPlan(Strict):
    start: date
    end: date
    calendar: CalendarProfile
    availability: dict[str, Availability] = Field(default_factory=dict, max_length=4)
    partition_days: int = Field(default=366, ge=1, le=366)
    max_requests: int = Field(default=4, ge=1, le=128)

    @model_validator(mode="after")
    def coherent(self):
        if not date(2000, 1, 1) <= self.start <= self.end < date(2100, 1, 1):
            raise ValueError("Invalid historical range")
        if self.calendar.coverage_start > self.start or self.calendar.coverage_end < self.end:
            raise ValueError("Calendar must cover the entire requested range")
        return self


@dataclass(frozen=True)
class WorkItem:
    listing: Listing
    start: date
    end: date


@dataclass(frozen=True)
class CollectedSeries:
    listing: Listing
    requested_start: date
    requested_end: date
    plan_fingerprint: str
    chunks: tuple[DailyResult, ...] = field(repr=False)
    unavailable_before_inception: tuple[date, date] | None = None
    availability: Availability | None = None

    @property
    def observations(self) -> tuple[DailyObservation, ...]:
        return tuple(row for chunk in self.chunks for row in chunk.observations)

    @property
    def missing_sessions(self) -> tuple[date, ...]:
        return tuple(
            sorted(
                {day for chunk in self.chunks for day in chunk.validation.missing_sessions or ()}
            )
        )

    def safe_summary(self):
        return plain(
            {
                "listing": self.listing.__dict__,
                "requested_start": self.requested_start,
                "requested_end": self.requested_end,
                "observations": len(self.observations),
                "missing_sessions": self.missing_sessions,
                "unavailable_before_inception": self.unavailable_before_inception,
                "availability": self.availability.model_dump(mode="json")
                if self.availability
                else None,
                "chunks": [r.safe_summary() for r in self.chunks],
                "source_qualified": False,
            }
        )


@dataclass(frozen=True)
class CollectionResult:
    status: str
    attempted_requests: int
    series: tuple[CollectedSeries, ...] = field(default=(), repr=False)
    failure_code: str | None = None
    failed_symbol: str | None = None
    unattempted_symbols: tuple[str, ...] = ()

    def safe_summary(self):
        return plain(
            {
                "status": self.status,
                "attempted_requests": self.attempted_requests,
                "series": [s.safe_summary() for s in self.series],
                "failure_code": self.failure_code,
                "failed_symbol": self.failed_symbol,
                "unattempted_symbols": self.unattempted_symbols,
            }
        )


def work_items(provider: DailyMarketDataProvider, plan: HistoryPlan) -> tuple[WorkItem, ...]:
    # Revalidate snapshots: a caller must not bypass validation using model_construct/copy.
    plan = HistoryPlan.model_validate(plan.model_dump())
    listings = provider.listings()
    if (
        len(listings) != 4
        or len(set(listings)) != 4
        or set(plan.availability) - {x.isin for x in listings}
    ):
        raise ValueError("Invalid listing or availability set")
    items = []
    for listing in listings:
        availability = plan.availability.get(listing.isin)
        lower = max(plan.start, availability.inception_date) if availability else plan.start
        while lower <= plan.end:
            upper = min(plan.end, lower + timedelta(days=plan.partition_days - 1))
            items.append(WorkItem(listing, lower, upper))
            if len(items) > plan.max_requests:
                raise ValueError("Request budget exceeded")
            lower = upper + timedelta(days=1)
    return tuple(items)


def preflight(provider: DailyMarketDataProvider, plan: HistoryPlan) -> dict:
    items = work_items(provider, plan)
    identity = {
        "provider": provider.identity,
        "listings": [x.__dict__ for x in provider.listings()],
        "plan": plan.model_dump(mode="json"),
        "policy": "daily-collection-v1",
    }
    return plain(
        {
            "status": "PREFLIGHT_ONLY_NO_NETWORK_NO_DATABASE",
            "plan_fingerprint": digest(identity),
            "provider": provider.identity,
            "requested_start": plan.start,
            "requested_end": plan.end,
            "expected_sessions": len(
                [d for d in plan.calendar.session_dates if plan.start <= d <= plan.end]
            ),
            "expected_requests": len(items),
            "max_requests": plan.max_requests,
            "requests": [
                {
                    "listing": item.listing.__dict__,
                    "from_date": item.start,
                    "to_date_inclusive": item.end,
                    "provider_end_exclusive": item.end + timedelta(days=1),
                }
                for item in items
            ],
            "request_interval_seconds": 1,
            "automatic_retries": 0,
            "timestamp_policy": "UNIX_SECONDS_IST_CANDIDATE_V1",
            "timestamp_semantics_verified": False,
            "persistence": "BLOCKED_UNTIL_SOURCE_USE_RETENTION_AND_POLICY_REVIEW",
            "calendar_evidence": plan.calendar.evidence_ref,
        }
    )


def collect_history(
    provider: DailyMarketDataProvider,
    plan: HistoryPlan,
    *,
    request_approved: bool = False,
    pause: Callable[[float], None] = time.sleep,
) -> CollectionResult:
    if request_approved is not True:
        return CollectionResult("BLOCKED", 0, failure_code="EXPLICIT_REQUEST_APPROVAL_REQUIRED")
    try:
        plan = HistoryPlan.model_validate(plan.model_dump())
        pre = preflight(provider, plan)
        items = work_items(provider, plan)
    except (ValueError, TypeError, AttributeError):
        return CollectionResult("BLOCKED", 0, failure_code="INVALID_PLAN_OR_REQUEST_BUDGET")
    attempted, results, completed = 0, [], []
    for index, item in enumerate(items):
        try:
            if index:
                pause(1.0)
            result = provider.retrieve_daily(
                DailyRequest(
                    item.listing, item.start, item.end, plan.calendar.model_copy(deep=True)
                ),
                request_approved=True,
            )
        except Exception:
            return CollectionResult(
                "STOPPED",
                attempted,
                failure_code="PROVIDER_OR_CONTROL_ERROR",
                failed_symbol=item.listing.symbol,
                unattempted_symbols=tuple(
                    dict.fromkeys(x.listing.symbol for x in items[index + 1 :])
                ),
            )
        attempted += result.request_attempts
        results.append((item, result))
        if result.failure or result.status not in {
            "VALIDATED_UNQUALIFIED",
            "VALIDATED_WITH_GAPS_UNQUALIFIED",
            "EMPTY_UNQUALIFIED",
        }:
            return CollectionResult(
                "STOPPED",
                attempted,
                failure_code=result.failure.code if result.failure else "INVALID_PROVIDER_RESULT",
                failed_symbol=item.listing.symbol,
                unattempted_symbols=tuple(
                    dict.fromkeys(x.listing.symbol for x in items[index + 1 :])
                ),
            )
    for listing in provider.listings():
        chunks = tuple(r for item, r in results if item.listing == listing)
        rows = [row for chunk in chunks for row in chunk.observations]
        if len(rows) != len({row.trading_date for row in rows}):
            return CollectionResult(
                "STOPPED",
                attempted,
                failure_code="CROSS_PARTITION_DUPLICATE",
                failed_symbol=listing.symbol,
            )
        available = plan.availability.get(listing.isin)
        unavailable = (
            (plan.start, min(plan.end, available.inception_date - timedelta(days=1)))
            if available and available.inception_date > plan.start
            else None
        )
        completed.append(
            CollectedSeries(
                listing,
                plan.start,
                plan.end,
                pre["plan_fingerprint"],
                chunks,
                unavailable,
                available.model_copy(deep=True) if available else None,
            )
        )
    return CollectionResult("COLLECTED_UNQUALIFIED", attempted, tuple(completed))
