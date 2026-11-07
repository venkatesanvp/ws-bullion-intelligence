"""Step 5E provider-neutral transient quote/intraday contracts and session policy.

No network, ORM, secrets, wall-clock reads or trading interpretation.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Protocol
from .market_data import Listing, ProviderFailure

IST = timezone(timedelta(hours=5, minutes=30), "Asia/Kolkata")
INTERVALS = (1, 5, 15, 25, 60)
WARNINGS = (
    "TIMESTAMP_CONVENTION_PROVISIONALLY_CORROBORATED",
    "PRICE_ADJUSTMENT_UNQUALIFIED",
    "TRANSIENT_MEMORY_ONLY",
)


def session_state(at, calendar):
    local = at.astimezone(IST)
    if calendar is None or not calendar.coverage_start <= local.date() <= calendar.coverage_end:
        return "UNKNOWN_CALENDAR"
    if local.date() not in set(calendar.session_dates):
        return "NON_TRADING"
    if local.time() < time(9, 15):
        return "PRE_OPEN"
    return "OPEN" if local.time() < time(15, 30) else "CLOSED"


def regular_bounds(day):
    return (datetime.combine(day, time(9, 15), IST), datetime.combine(day, time(15, 30), IST))


@dataclass(frozen=True)
class MarketQuote:
    listing: Listing
    last_price: Decimal
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    previous_close: Decimal | None
    provider_close: Decimal | None
    volume: int | None
    last_trade_at: datetime | None
    retrieved_at: datetime
    previous_close_basis: str = "UNAVAILABLE"
    provider: str = "DHANHQ"
    classification: str = "LIVE_QUOTE"
    warnings: tuple[str, ...] = WARNINGS


@dataclass(frozen=True)
class IntradayCandle:
    listing: Listing
    start: datetime
    end: datetime
    interval: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    retrieved_at: datetime
    source_timestamp: str = field(repr=False)
    source_row: int = 0
    provider: str = "DHANHQ"
    classification: str = "INTRADAY_PROVISIONAL"
    quality: str = "VALIDATED_CANDIDATE"
    warnings: tuple[str, ...] = WARNINGS
    requested_start: date | None = None
    requested_end: date | None = None
    volume_semantics: str = "UNASSESSED"


@dataclass(frozen=True)
class SessionResult:
    request_attempts: int = 0
    http_status: int | None = None
    quotes: tuple[MarketQuote, ...] = field(default=(), repr=False)
    candles: tuple[IntradayCandle, ...] = field(default=(), repr=False)
    failure: ProviderFailure | None = None
    issues: tuple[str, ...] = ()

    def summary(self):
        return {
            "request_attempts": self.request_attempts,
            "http_status": self.http_status,
            "quotes": len(self.quotes),
            "candles": len(self.candles),
            "error": self.failure.code if self.failure else None,
            "issues": self.issues,
            "latest_provider_timestamp": max(
                (r.last_trade_at for r in self.quotes if r.last_trade_at), default=None
            )
            or max((r.start for r in self.candles), default=None),
            "retrieved_at": max((r.retrieved_at for r in self.quotes + self.candles), default=None),
        }


class MarketSessionProvider(Protocol):
    identity: str

    def listings(self) -> tuple[Listing, ...]: ...
    def retrieve_quotes(self) -> SessionResult: ...
    def retrieve_intraday(
        self, listing: Listing, interval: int, start: date, end: date
    ) -> SessionResult: ...
