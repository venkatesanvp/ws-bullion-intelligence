"""Synthetic independent references for VS01-T-11..14. Not market/backtest data."""

from datetime import date, timedelta
from decimal import Decimal, getcontext, ROUND_FLOOR
from fractions import Fraction
import random
import pytest
from app.analytics import Point, indicator_values


def points(values):
    return [
        Point(date(2026, 1, 1) + timedelta(days=i), Decimal(str(v))) for i, v in enumerate(values)
    ]


def exact_wire(value):
    # Independent integer division and ties-to-even; no production wire/Decimal arithmetic.
    if value is None:
        return None
    negative = value < 0
    numerator = abs(value.numerator) * 10**12
    whole, remainder = divmod(numerator, value.denominator)
    if remainder * 2 > value.denominator or (remainder * 2 == value.denominator and whole % 2):
        whole += 1
    sign = "-" if negative and whole else ""
    return f"{sign}{whole // 10**12}.{whole % 10**12:012d}"


def reference(values, method, n):
    prices = [Fraction(str(v)) for v in values]
    result = [None] * len(prices)
    if method == "SMA":
        for i in range(n - 1, len(prices)):
            result[i] = sum(prices[i - n + 1 : i + 1]) / n
    elif method == "EMA":
        if len(prices) >= n:
            result[n - 1] = sum(prices[:n]) / n
            # Closed-form weighted sum, independent of the implementation recurrence.
            a, decay = Fraction(2, n + 1), Fraction(n - 1, n + 1)
            for i in range(n, len(prices)):
                result[i] = result[n - 1] * decay ** (i - n + 1) + sum(
                    a * prices[j] * decay ** (i - j) for j in range(n, i + 1)
                )
    else:
        changes = [b - a for a, b in zip(prices, prices[1:])]
        initial_up = sum(max(x, 0) for x in changes[:n]) / n
        initial_down = sum(max(-x, 0) for x in changes[:n]) / n
        for i in range(n, len(prices)):
            decay = Fraction(n - 1, n)
            up = initial_up * decay ** (i - n) + sum(
                Fraction(max(changes[j], 0), n) * decay ** (i - j - 1) for j in range(n, i)
            )
            down = initial_down * decay ** (i - n) + sum(
                Fraction(max(-changes[j], 0), n) * decay ** (i - j - 1) for j in range(n, i)
            )
            result[i] = (
                None
                if up == down == 0
                else Fraction(100)
                if down == 0
                else Fraction(0)
                if up == 0
                else 100 * up / (up + down)
            )
    return [exact_wire(value) for value in result]


@pytest.mark.parametrize(
    "method,expected",
    [
        ("SMA", [None, "11.000000000000", "13.000000000000", "13.500000000000"]),
        ("EMA", [None, "11.000000000000", "13.000000000000", "13.000000000000"]),
        ("RSI", [None, None, "100.000000000000", "66.666666666667"]),
    ],
)
def test_documented_synthetic_vectors(method, expected):
    assert [v["value"] for v in indicator_values(points([10, 12, 14, 13]), method, 2)] == expected


@pytest.mark.parametrize(
    "method,n", [("SMA", 1), ("EMA", 1), ("SMA", 3), ("EMA", 3), ("RSI", 2), ("RSI", 7)]
)
def test_independent_fraction_reference(method, n):
    generator = random.Random(1729)
    values = [str(Decimal(generator.randrange(1000, 100000)) / 100) for _ in range(60)]
    assert [v["value"] for v in indicator_values(points(values), method, n)] == reference(
        values, method, n
    )


@pytest.mark.parametrize(
    "values,expected,reason",
    [
        ([10, 11, 12, 13], "100.000000000000", None),
        ([13, 12, 11, 10], "0.000000000000", None),
        ([10, 10, 10, 10], None, "FLAT_WINDOW"),
    ],
)
def test_rsi_edges(values, expected, reason):
    result = indicator_values(points(values), "RSI", 2)
    assert result[-1]["value"] == expected and result[-1]["reason"] == reason


@pytest.mark.parametrize(
    "method,n",
    [
        ("SMA", 0),
        ("EMA", -1),
        ("RSI", 1),
        ("RSI", True),
        ("EMA", 2.5),
        ("SMA", 10001),
        ("OTHER", 2),
    ],
)
def test_invalid_parameters(method, n):
    with pytest.raises(ValueError, match="INVALID_INDICATOR_PARAMETERS"):
        indicator_values(points([10, 11, 12]), method, n)


@pytest.mark.parametrize("method,n", [("SMA", 3), ("EMA", 3), ("RSI", 3)])
def test_short_empty_and_segment_warmup(method, n):
    rows = points([10, 12, 14, 13, 17, 18])
    result = indicator_values(rows, method, n, {rows[3].day: "KNOWN_DISCONTINUITY"})
    assert result[3]["value"] is None and result[3]["reason"] == "DISCONTINUITY"
    assert result[4]["value"] is None
    if method == "RSI":
        assert result[5]["value"] is None
    else:
        assert result[5]["seed_date"] == rows[5].day
    assert indicator_values([], method, n) == []
    assert all(v["value"] is None for v in indicator_values(rows[:2], method, n))


@pytest.mark.parametrize("method", ["SMA", "EMA", "RSI"])
def test_global_context_and_future_rows_do_not_change_prefix(method):
    rows = points([10, 12, 14, 13, 17, 18, 16])
    expected = indicator_values(rows[:5], method, 2)
    context = getcontext()
    original = context.copy()
    try:
        context.prec, context.rounding = 5, ROUND_FLOOR
        assert indicator_values(rows, method, 2)[:5] == expected
        assert context.prec == 5 and context.rounding == ROUND_FLOOR
    finally:
        context.prec, context.rounding = original.prec, original.rounding


def test_half_even_serialization_and_ordering():
    result = indicator_values(points(["1.0000000000", "1.0000000001"]), "SMA", 2)
    assert result[-1]["value"] == "1.000000000050"
    with pytest.raises(ValueError, match="OBSERVATION_ORDER_REQUIRED"):
        indicator_values(list(reversed(points([10, 11]))), "SMA", 1)
