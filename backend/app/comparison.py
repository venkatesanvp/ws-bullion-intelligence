"""Pure price-only common-date comparison. DC-06 / WI-08 / VS01-T-15/16."""

from dataclasses import dataclass
from datetime import date
from decimal import Context, ROUND_HALF_EVEN, localcontext
from .analytics import Point, validate_points, wire

METHOD_VERSION = "common-date-price-v1"


@dataclass(frozen=True)
class ResearchSeries:
    key: str
    currency: str
    basis: str
    data_class: str
    adjustment_definition_ref: str | None
    points: list[Point]


def compare_series(series: list[ResearchSeries], start: date, end: date):
    if not 2 <= len(series) <= 10 or len({s.key for s in series}) != len(series) or start > end:
        raise ValueError("INVALID_COMPARISON_PARAMETERS")
    for item in series:
        validate_points(item.points)
    reason = None
    if len({s.currency for s in series}) != 1:
        reason = "INCOMPATIBLE_CURRENCY"
    elif any(s.basis == "UNKNOWN" for s in series):
        reason = "BASIS_UNVERIFIED"
    elif len({s.basis for s in series}) != 1:
        reason = "INCOMPATIBLE_BASIS"
    elif len({s.data_class for s in series}) != 1:
        reason = "MIXED_DATA_CLASSES"
    elif series[0].basis == "PROVIDER_ADJUSTED" and (
        any(not s.adjustment_definition_ref for s in series)
        or len({s.adjustment_definition_ref for s in series}) != 1
    ):
        reason = "ADJUSTMENT_COMPATIBILITY_UNVERIFIED"
    mappings = [{p.day: p for p in s.points if start <= p.day <= end} for s in series]
    dates = sorted(set.intersection(*(set(mapping) for mapping in mappings))) if not reason else []
    if not reason:
        reason = (
            "NO_COMMON_DATES"
            if not dates
            else "INSUFFICIENT_COMMON_DATES"
            if len(dates) == 1
            else None
        )
    status = "AVAILABLE" if reason is None else "PARTIAL" if len(dates) == 1 else "UNAVAILABLE"
    result = {
        "status": status,
        "unavailable_reason": reason,
        "method_version": METHOD_VERSION,
        "requested_period": {"start": start, "end": end},
        "effective_period": {
            "start": dates[0] if dates else None,
            "end": dates[-1] if dates else None,
        },
        "common_dates": dates,
        "common_observation_count": len(dates),
        "series": [],
    }
    with localcontext(Context(prec=34, rounding=ROUND_HALF_EVEN)):
        for item, mapping in zip(series, mappings):
            first, last = (mapping[dates[0]], mapping[dates[-1]]) if dates else (None, None)
            change = wire(100 * (last.close / first.close - 1)) if len(dates) >= 2 else None
            values = [
                {
                    "trading_date": day,
                    "close": format(mapping[day].close, "f"),
                    "rebased_price": wire(100 * mapping[day].close / first.close)
                    if len(dates) >= 2
                    else None,
                    "volume": mapping[day].volume,
                    "observation_id": mapping[day].observation_id,
                    "batch_id": mapping[day].batch_id,
                    "row_number": mapping[day].row_number,
                }
                for day in dates
            ]
            result["series"].append(
                {
                    "key": item.key,
                    "currency": item.currency,
                    "price_basis": item.basis,
                    "data_class": item.data_class,
                    "close_end": format(last.close, "f") if last else None,
                    "volume_end": last.volume if last else None,
                    "price_change_percent": change,
                    "values": values,
                }
            )
    return result
