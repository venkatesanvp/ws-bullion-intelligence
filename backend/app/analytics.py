"""Pure Decimal research arithmetic. REQ-03-007 -> ADR-06/DC-05 -> WI-07.

No database, network, wall clock, global-context mutation or trading interpretation.
"""

from collections import deque
from dataclasses import dataclass
from datetime import date
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from typing import Literal

MAX_POINTS = 10_000
ALGORITHM_VERSION = "decimal-research-v1"
SCALE = Decimal("0.000000000001")


@dataclass(frozen=True)
class Point:
    day: date
    close: Decimal
    observation_id: str = ""
    canonical_hash: str = ""
    batch_id: str = ""
    row_number: int = 0
    volume: int | None = None


def validate_points(points):
    if len(points) > MAX_POINTS:
        raise ValueError("ANALYTICS_RANGE_LIMIT")
    previous = None
    for point in points:
        if not isinstance(point.close, Decimal) or not point.close.is_finite() or point.close <= 0:
            raise ValueError("INVALID_CLOSE")
        if previous is not None and point.day <= previous:
            raise ValueError("OBSERVATION_ORDER_REQUIRED")
        previous = point.day


def wire(value: Decimal) -> str:
    """Call within the explicit arithmetic context; retain twelve derived places."""
    result = value.quantize(SCALE)
    return format(abs(result) if result.is_zero() else result, "f")


def indicator_values(
    points: list[Point],
    indicator: Literal["SMA", "EMA", "RSI"],
    n: int,
    breaks: dict[date, str] | None = None,
):
    minimum = 2 if indicator == "RSI" else 1
    if (
        indicator not in {"SMA", "EMA", "RSI"}
        or type(n) is not int
        or not minimum <= n <= MAX_POINTS
    ):
        raise ValueError("INVALID_INDICATOR_PARAMETERS")
    validate_points(points)
    breaks = breaks or {}
    output = []
    with localcontext(Context(prec=34, rounding=ROUND_HALF_EVEN)):
        window = deque()
        total = Decimal(0)
        ema = previous = gain = loss = None
        gains = losses = Decimal(0)
        delta_count = 0
        seed_date = None
        for point in points:
            boundary = breaks.get(point.day)
            if boundary:
                window.clear()
                total = Decimal(0)
                ema = previous = gain = loss = None
                gains = losses = Decimal(0)
                delta_count = 0
                seed_date = None
            value = None
            reason = "DISCONTINUITY" if boundary else "WARMUP"
            if indicator in {"SMA", "EMA"}:
                window.append(point.close)
                total += point.close
                if len(window) > n:
                    total -= window.popleft()
                if len(window) == n:
                    if seed_date is None:
                        seed_date = point.day
                    if indicator == "SMA":
                        value = total / n
                    elif ema is None:
                        ema = total / n
                        value = ema
                    else:
                        alpha = Decimal(2) / (n + 1)
                        ema = alpha * point.close + (1 - alpha) * ema
                        value = ema
            else:
                if previous is not None:
                    delta = point.close - previous
                    up, down = max(delta, Decimal(0)), max(-delta, Decimal(0))
                    delta_count += 1
                    if gain is None:
                        gains += up
                        losses += down
                        if delta_count == n:
                            gain, loss = gains / n, losses / n
                            seed_date = point.day
                    else:
                        gain = ((n - 1) * gain + up) / n
                        loss = ((n - 1) * loss + down) / n
                    if gain is not None:
                        if gain == 0 and loss == 0:
                            reason = "FLAT_WINDOW"
                        elif loss == 0:
                            value = Decimal(100)
                        elif gain == 0:
                            value = Decimal(0)
                        else:
                            value = 100 - Decimal(100) / (1 + gain / loss)
                previous = point.close
            output.append(
                {
                    "trading_date": point.day,
                    "value": wire(value) if value is not None else None,
                    "reason": None if value is not None else reason,
                    "seed_date": seed_date,
                    "break_before": boundary,
                }
            )
    return output
