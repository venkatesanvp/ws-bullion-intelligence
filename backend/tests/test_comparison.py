"""Synthetic price-only vectors; independent exact-rational checks. VS01-T-15/16."""

from datetime import date, timedelta
from decimal import Decimal, getcontext, ROUND_FLOOR
from fractions import Fraction
from dataclasses import replace
import pytest
from app.analytics import Point
from app.comparison import ResearchSeries, compare_series
from .test_analytics import exact_wire

START, END = date(2026, 1, 1), date(2026, 1, 5)


def series(key, values, days=(0, 1, 2), **kwargs):
    return ResearchSeries(
        key,
        kwargs.get("currency", "INR"),
        kwargs.get("basis", "RAW_CLOSE"),
        kwargs.get("data_class", "SYNTHETIC_TEST"),
        kwargs.get("adjustment_definition_ref"),
        [
            Point(START + timedelta(days=d), Decimal(str(v)), volume=None)
            for d, v in zip(days, values)
        ],
    )


def test_common_date_reference_and_real_endpoints():
    a, b = series("a", [10, 11, 12]), series("b", [20, 22, 23])
    result = compare_series([a, b], START, END)
    assert [s["price_change_percent"] for s in result["series"]] == [
        "20.000000000000",
        "15.000000000000",
    ]
    assert result["effective_period"] == {"start": START, "end": START + timedelta(days=2)}
    assert result["series"][1]["values"][-1]["rebased_price"] == "115.000000000000"
    assert result["series"][0]["volume_end"] is None
    for item, source in zip(result["series"], [a, b]):
        expected = 100 * (Fraction(source.points[-1].close) / Fraction(source.points[0].close) - 1)
        assert item["price_change_percent"] == exact_wire(expected)


def test_sparse_intersection_and_explicit_period_no_fill():
    result = compare_series(
        [series("a", [10, 11, 12]), series("b", [20, 23], days=(0, 2))], START, END
    )
    assert result["common_dates"] == [START, START + timedelta(days=2)]
    assert all(len(s["values"]) == 2 for s in result["series"])
    single = compare_series(
        [series("a", [10, 11, 12]), series("b", [20, 23], days=(0, 2))],
        START + timedelta(days=1),
        END,
    )
    assert (
        single["status"] == "PARTIAL"
        and single["unavailable_reason"] == "INSUFFICIENT_COMMON_DATES"
    )
    assert all(s["price_change_percent"] is None for s in single["series"])
    assert single["series"][0]["close_end"] == "12"
    empty = compare_series([series("a", [10]), series("b", [20], days=(1,))], START, END)
    assert empty["unavailable_reason"] == "NO_COMMON_DATES" and empty["common_dates"] == []


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"currency": "USD"}, "INCOMPATIBLE_CURRENCY"),
        ({"basis": "UNKNOWN"}, "BASIS_UNVERIFIED"),
        ({"basis": "PROVIDER_ADJUSTED"}, "INCOMPATIBLE_BASIS"),
        ({"data_class": "REAL_MARKET"}, "MIXED_DATA_CLASSES"),
    ],
)
def test_incompatible_inputs_unavailable(change, reason):
    result = compare_series(
        [series("a", [10, 11]), replace(series("b", [20, 22]), **change)], START, END
    )
    assert result["status"] == "UNAVAILABLE" and result["unavailable_reason"] == reason
    assert all(s["price_change_percent"] is None and not s["values"] for s in result["series"])


def test_adjustment_definitions_require_recorded_compatibility():
    a, b = (
        series(
            "a",
            [10, 11],
            basis="PROVIDER_ADJUSTED",
            adjustment_definition_ref="SYNTHETIC SAME DEFINITION",
        ),
        series(
            "b", [20, 22], basis="PROVIDER_ADJUSTED", adjustment_definition_ref="OTHER DEFINITION"
        ),
    )
    assert (
        compare_series([a, b], START, END)["unavailable_reason"]
        == "ADJUSTMENT_COMPATIBILITY_UNVERIFIED"
    )
    assert (
        compare_series(
            [a, replace(b, adjustment_definition_ref=a.adjustment_definition_ref)], START, END
        )["status"]
        == "AVAILABLE"
    )


def test_negative_change_and_global_context():
    a, b = series("a", [3, 2]), series("b", [7, 5])
    expected = compare_series([a, b], START, END)
    saved = getcontext().copy()
    try:
        getcontext().prec, getcontext().rounding = 5, ROUND_FLOOR
        assert compare_series([a, b], START, END) == expected
        assert getcontext().prec == 5
    finally:
        getcontext().prec, getcontext().rounding = saved.prec, saved.rounding
    assert expected["series"][0]["price_change_percent"] == exact_wire(Fraction(-100, 3))


@pytest.mark.parametrize(
    "items,start,end",
    [
        ([series("a", [10])], START, END),
        ([series("a", [10]), series("a", [20])], START, END),
        ([series("a", [10]), series("b", [20])], END, START),
    ],
)
def test_invalid_comparisons(items, start, end):
    with pytest.raises(ValueError, match="INVALID_COMPARISON_PARAMETERS"):
        compare_series(items, start, end)
