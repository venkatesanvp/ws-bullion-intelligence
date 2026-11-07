"""Independent Fraction/closed-form vectors for Package 2B; synthetic data only."""

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal, getcontext
from fractions import Fraction
import random
import pytest
from app.technical_analytics import CandlePoint, TechnicalParameters, technical_values
from .test_analytics import exact_wire


def rows(values):
    return [
        CandlePoint(
            date(2026, 1, 1) + timedelta(days=i),
            Decimal(str(v)),
            Decimal(str(v)),
            Decimal(str(v)) + 1,
            Decimal(str(v)) - 1,
            1000,
        )
        for i, v in enumerate(values)
    ]


def fraction_ema(values, n):
    values = [Fraction(str(x)) for x in values]
    output = [None] * len(values)
    alpha, decay = Fraction(2, n + 1), Fraction(n - 1, n + 1)
    if len(values) >= n:
        seed = sum(values[:n]) / n
        for i in range(n - 1, len(values)):
            output[i] = seed * decay ** (i - n + 1) + sum(
                alpha * values[j] * decay ** (i - j) for j in range(n, i + 1)
            )
    return output


def test_hand_calculated_seed_and_current_bar_exclusion():
    data = rows([10, 11, 12, 14, 13])
    p = TechnicalParameters(atr_n=3, macd_fast=2, macd_slow=3, macd_signal=2, donchian_n=3)
    out = technical_values(data, p)
    assert [v["value"] for v in out["ATR"]["values"]] == [
        None,
        None,
        None,
        "2.333333333333",
        "2.222222222222",
    ]
    m = out["MACD"]["values"]
    assert m[2]["macd"] == "0.500000000000" and m[2]["signal"] is None
    assert m[3]["macd"] == exact_wire(Fraction(2, 3)) and m[3]["signal"] == exact_wire(
        Fraction(7, 12)
    )
    assert m[3]["histogram"] == exact_wire(Fraction(1, 12))
    assert m[4]["signal"] == exact_wire(Fraction(43, 108)) and m[4]["histogram"] == exact_wire(
        -Fraction(5, 54)
    )
    d = out["DONCHIAN"]["values"]
    assert d[3]["upper"] == "13.000000000000" and d[3]["lower"] == "9.000000000000"
    spike = data[:3] + [replace(data[3], high=Decimal(1000))] + data[4:]
    assert technical_values(spike, p)["DONCHIAN"]["values"][3] == d[3]
    assert out["ATR"]["values"][3]["seed_date"] == data[3].time
    assert m[3]["signal_seed_date"] == data[3].time


@pytest.mark.parametrize(
    "n,fast,slow,signal", [(1, 1, 2, 1), (3, 2, 5, 3), (14, 12, 26, 9), (20, 5, 40, 7)]
)
def test_independent_fraction_references_and_prefix_invariance(n, fast, slow, signal):
    rng = random.Random(42)
    values = [100 + Fraction(rng.randrange(-100, 100), 100) for _ in range(120)]
    data = rows([Decimal(v.numerator) / v.denominator for v in values])
    p = TechnicalParameters(
        atr_n=n, macd_fast=fast, macd_slow=slow, macd_signal=signal, donchian_n=n
    )
    out = technical_values(data, p)
    f, s = (
        fraction_ema([r.close for r in data], fast),
        fraction_ema([r.close for r in data], slow),
    )
    macd = [f[i] - s[i] for i in range(slow - 1, len(data))]
    sig = fraction_ema(macd, signal)
    for i, v in enumerate(out["MACD"]["values"]):
        if i < slow - 1:
            assert v["macd"] is None
        else:
            j = i - slow + 1
            assert v["macd"] == exact_wire(macd[j])
            assert v["signal"] == exact_wire(sig[j])
            assert (
                v["histogram"] == exact_wire(macd[j] - sig[j])
                if sig[j] is not None
                else v["histogram"] is None
            )
    trs = [
        max(
            Fraction(b.high - b.low),
            abs(Fraction(b.high - a.close)),
            abs(Fraction(b.low - a.close)),
        )
        for a, b in zip(data, data[1:])
    ]
    decay = Fraction(n - 1, n)
    seed = sum(trs[:n]) / n
    for i, v in enumerate(out["ATR"]["values"]):
        expected = (
            None
            if i < n
            else seed * decay ** (i - n)
            + sum(trs[j] * Fraction(1, n) * decay ** (i - j - 1) for j in range(n, i))
        )
        assert v["value"] == exact_wire(expected)
    for i, v in enumerate(out["DONCHIAN"]["values"]):
        assert v["upper"] == (
            exact_wire(max(Fraction(r.high) for r in data[i - n : i])) if i >= n else None
        )
        assert v["lower"] == (
            exact_wire(min(Fraction(r.low) for r in data[i - n : i])) if i >= n else None
        )
    shorter = technical_values(data[:75], p)
    assert all(shorter[k]["values"] == out[k]["values"][:75] for k in out)


def test_flat_values_missing_ohlc_and_independent_macd():
    data = rows([10] * 50)
    out = technical_values(data)
    assert out["ATR"]["values"][14]["value"] == "2.000000000000"
    assert out["MACD"]["values"][33]["histogram"] == "0.000000000000"
    absent = [replace(r, open=None, high=None, low=None) for r in data]
    out2 = technical_values(absent)
    assert out2["MACD"] == out["MACD"]
    assert all(v["reason"] == "MISSING_OHLC" for v in out2["ATR"]["values"])
    assert all(v["upper"] is None for v in out2["DONCHIAN"]["values"])


def test_discontinuity_restarts_all_seeds_and_missing_ohlc_only_restarts_ohlc_methods():
    data = rows(range(10, 90))
    p = TechnicalParameters(atr_n=3, macd_fast=2, macd_slow=3, macd_signal=2, donchian_n=3)
    cut = 30
    out = technical_values(data, p, {data[cut].time: "KNOWN_MISSING_SESSION"})
    suffix = technical_values(data[cut:], p)
    for name in out:
        assert out[name]["values"][cut]["break_before"] == "KNOWN_MISSING_SESSION"
        assert out[name]["values"][cut + 1 :] == suffix[name]["values"][1:]
    missing = data.copy()
    missing[cut] = replace(missing[cut], open=None, high=None, low=None)
    missing_out = technical_values(missing, p)
    assert missing_out["MACD"] == technical_values(data, p)["MACD"]
    assert missing_out["ATR"]["values"][cut + 3]["value"] is None
    assert missing_out["ATR"]["values"][cut + 4]["value"] is not None


def test_incomplete_observations_never_contribute():
    data = rows(range(10, 70))
    p = TechnicalParameters(atr_n=2, macd_fast=1, macd_slow=2, macd_signal=1, donchian_n=2)
    data[30] = replace(data[30], completed=False)
    out = technical_values(data, p)
    assert all(out[name]["values"][30]["reason"] == "INCOMPLETE_OBSERVATION" for name in out)
    assert (
        out["ATR"]["values"][32]["value"] is None and out["ATR"]["values"][33]["value"] is not None
    )
    assert out["MACD"]["values"][31]["macd"] is None


@pytest.mark.parametrize(
    "config",
    [
        {"atr_n": 0},
        {"atr_n": True},
        {"atr_n": 1.5},
        {"macd_fast": 26},
        {"macd_slow": 12},
        {"macd_signal": 10000},
        {"donchian_n": 10000},
        {"rsi_n": 1},
    ],
)
def test_invalid_periods_and_warmup_bounds(config):
    with pytest.raises(ValueError):
        TechnicalParameters(**config)


@pytest.mark.parametrize(
    "defect",
    [
        "float",
        "nan",
        "negative",
        "partial_ohlc",
        "inconsistent_ohlc",
        "volume",
        "order",
        "duplicate",
    ],
)
def test_rejects_invalid_values_without_truncation(defect):
    data = rows([10, 11, 12])
    if defect == "float":
        data[0] = replace(data[0], close=10.0)
    if defect == "nan":
        data[0] = replace(data[0], close=Decimal("NaN"))
    if defect == "negative":
        data[0] = replace(data[0], close=Decimal(-1))
    if defect == "partial_ohlc":
        data[0] = replace(data[0], high=None)
    if defect == "inconsistent_ohlc":
        data[0] = replace(data[0], high=Decimal(1))
    if defect == "volume":
        data[0] = replace(data[0], volume=True)
    if defect == "order":
        data.reverse()
    if defect == "duplicate":
        data[1] = data[0]
    with pytest.raises(ValueError):
        technical_values(data)


def test_empty_limit_and_decimal_context_isolation():
    assert all(not bundle["values"] for bundle in technical_values([]).values())
    data = rows([10] * 10001)
    with pytest.raises(ValueError, match="RANGE_LIMIT"):
        technical_values(data)
    data = data[:60]
    expected = technical_values(data)
    old = getcontext().prec
    try:
        getcontext().prec = 6
        assert technical_values(data) == expected and getcontext().prec == 6
    finally:
        getcontext().prec = old
