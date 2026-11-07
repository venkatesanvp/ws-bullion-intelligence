"""Package 2B pure Decimal ATR/MACD/prior-window Donchian. No I/O or forecasts."""

from collections import deque
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from .analytics import MAX_POINTS, Point, validate_points, wire
from .schemas import Strict
from pydantic import Field, model_validator

VERSION = "decimal-technical-v1"


class TechnicalParameters(Strict):
    atr_n: int = Field(default=14, strict=True, ge=1, le=9999)
    macd_fast: int = Field(default=12, strict=True, ge=1, le=9999)
    macd_slow: int = Field(default=26, strict=True, ge=2, le=10000)
    macd_signal: int = Field(default=9, strict=True, ge=1, le=9999)
    donchian_n: int = Field(default=20, strict=True, ge=1, le=9999)
    sma_n: int = Field(default=20, strict=True, ge=1, le=10000)
    ema_n: int = Field(default=37, strict=True, ge=1, le=10000)
    rsi_n: int = Field(default=14, strict=True, ge=2, le=9999)

    @model_validator(mode="after")
    def periods(self):
        if self.macd_fast >= self.macd_slow or self.macd_slow + self.macd_signal - 1 > MAX_POINTS:
            raise ValueError("INVALID_MACD_PERIODS")
        return self

    def warmup(self):
        return max(
            self.atr_n + 1,
            self.macd_slow + self.macd_signal - 1,
            self.donchian_n + 1,
            self.sma_n,
            self.ema_n,
            self.rsi_n + 1,
        )


@dataclass(frozen=True)
class CandlePoint:
    time: date | datetime
    close: Decimal
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    volume: int | None = None
    completed: bool = True


class Ema:
    def __init__(self, n):
        self.n, self.count, self.total, self.value = n, 0, Decimal(0), None

    def push(self, value):
        self.count += 1
        if self.value is None:
            self.total += value
            if self.count == self.n:
                self.value = self.total / self.n
        else:
            alpha = Decimal(2) / (self.n + 1)
            self.value = alpha * value + (1 - alpha) * self.value
        return self.value


def validate_candles(rows):
    validate_points([Point(r.time, r.close) for r in rows])
    for row in rows:
        fields = (row.open, row.high, row.low)
        if any(v is not None for v in fields):
            if not all(isinstance(v, Decimal) and v.is_finite() and v > 0 for v in fields):
                raise ValueError("INVALID_OHLC")
            if not row.low <= row.open <= row.high or not row.low <= row.close <= row.high:
                raise ValueError("INCONSISTENT_OHLC")
        if row.volume is not None and (type(row.volume) is not int or row.volume < 0):
            raise ValueError("INVALID_VOLUME")
        if type(row.completed) is not bool:
            raise ValueError("INVALID_COMPLETENESS")


def technical_values(rows, parameters=None, breaks=None):
    parameters = parameters or TechnicalParameters()
    if not isinstance(parameters, TechnicalParameters):
        parameters = TechnicalParameters.model_validate(parameters)
    validate_candles(rows)
    breaks = breaks or {}
    result = {name: [] for name in ("ATR", "MACD", "DONCHIAN")}
    with localcontext(Context(prec=34, rounding=ROUND_HALF_EVEN)):
        fast, slow, signal = (
            Ema(parameters.macd_fast),
            Ema(parameters.macd_slow),
            Ema(parameters.macd_signal),
        )
        tr = deque(maxlen=parameters.atr_n)
        prior = deque(maxlen=parameters.donchian_n)
        previous = atr = atr_seed = macd_seed = signal_seed = channel_seed = None
        for row in rows:
            boundary = breaks.get(row.time)
            if boundary or not row.completed:
                fast, slow, signal = (
                    Ema(parameters.macd_fast),
                    Ema(parameters.macd_slow),
                    Ema(parameters.macd_signal),
                )
                tr.clear()
                prior.clear()
                previous = atr = atr_seed = macd_seed = signal_seed = channel_seed = None
            reason = (
                "INCOMPLETE_OBSERVATION"
                if not row.completed
                else "DISCONTINUITY"
                if boundary
                else "WARMUP"
            )
            atr_value = macd_value = signal_value = histogram = upper = lower = middle = None
            ohlc = row.open is not None
            if row.completed:
                f, s = fast.push(row.close), slow.push(row.close)
                if s is not None:
                    macd_value = f - s
                    macd_seed = macd_seed or row.time
                    signal_value = signal.push(macd_value)
                    if signal_value is not None:
                        signal_seed = signal_seed or row.time
                        histogram = macd_value - signal_value
                if not ohlc:
                    tr.clear()
                    prior.clear()
                    previous = atr = atr_seed = channel_seed = None
                else:
                    if previous is not None:
                        value = max(
                            row.high - row.low, abs(row.high - previous), abs(row.low - previous)
                        )
                        tr.append(value)
                        if atr is not None:
                            atr = ((parameters.atr_n - 1) * atr + value) / parameters.atr_n
                        elif len(tr) == parameters.atr_n:
                            atr = sum(tr, Decimal(0)) / parameters.atr_n
                            atr_seed = row.time
                        atr_value = atr
                    previous = row.close
                    if len(prior) == parameters.donchian_n:
                        upper, lower = max(r.high for r in prior), min(r.low for r in prior)
                        middle = (upper + lower) / 2
                        channel_seed = channel_seed or row.time
                    prior.append(row)  # Current candle never enters its own breakout reference.

            def encoded(value):
                return wire(value) if value is not None else None

            result["ATR"].append(
                {
                    "time": row.time,
                    "value": encoded(atr_value),
                    "reason": None
                    if atr_value is not None
                    else "MISSING_OHLC"
                    if row.completed and not ohlc
                    else reason,
                    "seed_date": atr_seed,
                    "break_before": boundary,
                }
            )
            result["MACD"].append(
                {
                    "time": row.time,
                    "macd": encoded(macd_value),
                    "signal": encoded(signal_value),
                    "histogram": encoded(histogram),
                    "reason": None if histogram is not None else reason,
                    "line_reason": None if macd_value is not None else reason,
                    "seed_date": macd_seed,
                    "signal_seed_date": signal_seed,
                    "break_before": boundary,
                }
            )
            result["DONCHIAN"].append(
                {
                    "time": row.time,
                    "upper": encoded(upper),
                    "lower": encoded(lower),
                    "middle": encoded(middle),
                    "reason": None
                    if upper is not None
                    else "MISSING_OHLC"
                    if row.completed and not ohlc
                    else reason,
                    "seed_date": channel_seed,
                    "break_before": boundary,
                }
            )
    return {
        name: {
            "algorithm_version": VERSION,
            "parameters": parameters.model_dump(),
            "values": values,
        }
        for name, values in result.items()
    }
