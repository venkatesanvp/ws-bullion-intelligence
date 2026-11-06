"""Read-only Dhan binary quote decoder. Exact IEEE-754 -> unique verified tick.

No Python float conversion or financial float arithmetic. Protocol: official v2
live-market-feed/annexure. Tick metadata: NSE/E master, 2026-11-06; paise per
Dhan support FAQ. Reject wire prices compatible with multiple exchange ticks.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
import struct
from .market_session import IST
from .dhan_history_contract import INSTRUMENTS, MIN_CANDIDATE_SECONDS, MAX_CANDIDATE_SECONDS


def exact_float32(bits):
    exponent, mantissa = (bits >> 23) & 255, bits & 0x7FFFFF
    if bits >> 31 or exponent == 255:
        raise ValueError("INVALID_WIRE_PRICE")
    with localcontext() as context:
        context.prec = 200
        power = exponent - 150 if exponent else -149
        return Decimal(mantissa + (1 << 23 if exponent else 0)) * Decimal(2) ** power


def tick_price(packet, offset, tick, *, optional=False):
    bits = struct.unpack_from("<I", packet, offset)[0]
    value = exact_float32(bits)
    if value == 0 and optional:
        return None
    if value <= 0 or value >= Decimal("1e14") or tick is None or tick <= 0:
        raise ValueError("INVALID_WIRE_PRICE")
    with localcontext() as context:
        context.prec = 200
        lo = (value + exact_float32(bits - 1)) / 2
        hi = (value + exact_float32(bits + 1)) / 2
        candidate = (value / tick).to_integral_value(rounding=ROUND_HALF_EVEN) * tick
        # Conservative closed intervals: ties or multiple ticks are not guessed.
        if not lo <= candidate <= hi or candidate - tick >= lo or candidate + tick <= hi:
            raise ValueError("AMBIGUOUS_WIRE_PRICE")
        return candidate


@dataclass(frozen=True)
class FeedEvent:
    code: int
    symbol: str | None = None
    isin: str | None = None
    received_at: datetime | None = None
    trade_at: datetime | None = None
    prices: dict = field(default_factory=dict, repr=False)
    volume: int | None = None
    disconnect_code: int | None = None
    wire_epoch_seconds: int | None = None


def decode(packet, received_at, *, catalog=INSTRUMENTS):
    if not isinstance(packet, bytes) or not 8 <= len(packet) <= 4096:
        raise ValueError("INVALID_FEED_FRAME")
    code, length, segment, security_id = struct.unpack_from("<BHBi", packet)
    if length != len(packet):
        raise ValueError("INVALID_FEED_LENGTH")
    if code == 50:
        if len(packet) != 10:
            raise ValueError("INVALID_FEED_LENGTH")
        return FeedEvent(code, disconnect_code=struct.unpack_from("<H", packet, 8)[0])
    item = next((x for x in catalog if x.security_id == str(security_id)), None)
    if segment != 1 or item is None:
        raise ValueError("UNSUBSCRIBED_FEED_IDENTITY")
    sizes = {2: 16, 4: 50, 6: 16, 5: 12}
    if code not in sizes or sizes[code] != len(packet):
        raise ValueError("UNSUPPORTED_FEED_STRUCTURE")
    tick = Decimal(item.tick_size_paise) / 100 if item.tick_size_paise else None
    if code == 5:
        return FeedEvent(code, item.symbol, item.isin, received_at)
    if code == 6:
        return FeedEvent(
            code,
            item.symbol,
            item.isin,
            received_at,
            prices={"previous_close": tick_price(packet, 8, tick)},
        )
    epoch = struct.unpack_from("<i", packet, 12 if code == 2 else 14)[0]
    if not MIN_CANDIDATE_SECONDS <= epoch <= MAX_CANDIDATE_SECONDS:
        raise ValueError("INVALID_FEED_TIMESTAMP")
    # Explicit feed-specific candidate, not fallback/unit inference. Official SDK
    # utc_time renders UTC clock fields without converting them; the four 2026-11-06
    # feed clock fields match independently retrieved REST IST LTTs exactly.
    # Preserve wire seconds; do not apply this convention to history endpoints.
    trade_at = datetime.fromtimestamp(epoch, timezone.utc).replace(tzinfo=IST)
    if trade_at > received_at + timedelta(seconds=5):
        raise ValueError("FUTURE_FEED_TIMESTAMP")
    prices = {"last_price": tick_price(packet, 8, tick)}
    volume = None
    if code == 4:
        volume = struct.unpack_from("<i", packet, 22)[0]
        if volume < 0:
            raise ValueError("INVALID_FEED_VOLUME")
        for name, offset in (("open", 34), ("provider_close", 38), ("high", 42), ("low", 46)):
            prices[name] = tick_price(packet, offset, tick, optional=True)
        op, hi, lo = (prices[k] for k in ("open", "high", "low"))
        if (
            hi is not None
            and lo is not None
            and (
                lo > hi
                or op is not None
                and not lo <= op <= hi
                or not lo <= prices["last_price"] <= hi
            )
        ):
            raise ValueError("INCONSISTENT_FEED_OHLC")
    return FeedEvent(
        code,
        item.symbol,
        item.isin,
        received_at,
        trade_at,
        prices,
        volume,
        wire_epoch_seconds=epoch,
    )
