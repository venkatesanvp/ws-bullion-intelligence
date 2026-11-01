"""Snapshot-consistent research APIs. DC-04..08; WI-07/08/10.

Read-only orchestration: authoritative values come from the pure Decimal engines.
"""

from bisect import bisect_right
from datetime import date, datetime
from decimal import DecimalException
from typing import Annotated, Literal
from uuid import UUID
from fastapi import Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from .analytics import ALGORITHM_VERSION, MAX_POINTS, Point, indicator_values
from .comparison import METHOD_VERSION, ResearchSeries, compare_series
from .errors import APIError
from .models import Observation, now
from .queries import series, series_meta
from .schemas import ComparisonRequest
from .serialization import digest

Basis = Literal["RAW_CLOSE", "PROVIDER_ADJUSTED", "UNKNOWN"]


def bounded_points(db, instrument_id, source_id, basis, start=None, end=None):
    statement = select(Observation).where(
        Observation.instrument_id == instrument_id,
        Observation.source_id == source_id,
        Observation.price_basis == basis,
        Observation.interval == "1d",
    )
    if start:
        statement = statement.where(Observation.trading_date >= start)
    if end:
        statement = statement.where(Observation.trading_date <= end)
    rows = list(
        db.scalars(
            statement.order_by(Observation.trading_date, Observation.id).limit(MAX_POINTS + 1)
        )
    )
    if len(rows) > MAX_POINTS:
        raise APIError(
            422,
            "ANALYTICS_RANGE_LIMIT",
            "The complete research input exceeds 10,000 observations. Use history inspection or a supported range; no prefix was truncated.",
        )
    return [
        Point(
            r.trading_date,
            r.close,
            str(r.id),
            r.canonical_hash,
            str(r.batch_id),
            r.row_number,
            r.volume,
        )
        for r in rows
    ]


def breaks_for(points, profile):
    declared = sorted(profile.get("known_break_dates", []))
    calendar = profile.get("calendar")
    sessions = sorted(calendar["session_dates"]) if calendar else []
    breaks = {}
    for previous, point in zip(points, points[1:]):
        reasons = []
        index = bisect_right(declared, previous.day.isoformat())
        if index < len(declared) and declared[index] <= point.day.isoformat():
            reasons.append("KNOWN_DISCONTINUITY")
        index = bisect_right(sessions, previous.day.isoformat())
        if index < len(sessions) and sessions[index] < point.day.isoformat():
            reasons.append("KNOWN_MISSING_SESSION")
        if reasons:
            breaks[point.day] = ",".join(reasons)
    if points and points[0].day.isoformat() in declared:
        breaks[points[0].day] = "KNOWN_DISCONTINUITY"
    return breaks


def evidence(points):
    return {
        "observation_count": len(points),
        "first_date": points[0].day if points else None,
        "last_date": points[-1].day if points else None,
        "batch_ids": sorted({p.batch_id for p in points}),
    }


def input_identity(points):
    return [
        {
            "observation_id": p.observation_id,
            "canonical_hash": p.canonical_hash,
            "trading_date": p.day,
            "close": p.close,
        }
        for p in points
    ]


def validate_range(start, end):
    if start is not None and end is not None and start > end:
        raise APIError(422, "INVALID_RANGE", "Start date must be on or before end date.")


def register_research(router, get_db, respond):
    DB = Annotated[Session, Depends(get_db)]

    @router.get("/instruments/{instrument_id}/chart")
    def chart(
        instrument_id: UUID,
        source_id: UUID,
        basis: Basis,
        request: Request,
        db: DB,
        start: date | None = None,
        end: date | None = None,
        assessment_as_of: datetime | None = None,
    ):
        validate_range(start, end)
        instrument, source = series(db, instrument_id, source_id)
        points = bounded_points(db, instrument_id, source_id, basis, start, end)
        meta = series_meta(db, instrument, source, basis, start, end, assessment_as_of)
        breaks = breaks_for(points, source.profile)
        data = {
            "status": "AVAILABLE" if points else "UNAVAILABLE",
            "unavailable_reason": None if points else "NO_HISTORY",
            "series_ref": meta["series_ref"],
            "computed_at": now(),
            "input_evidence": evidence(points),
            "input_fingerprint": digest(
                {
                    "method": "price-chart-v1",
                    "series": meta["series_ref"],
                    "start": start,
                    "end": end,
                    "points": input_identity(points),
                }
            ),
            "points": [
                {
                    "trading_date": p.day,
                    "close": p.close,
                    "observation_id": p.observation_id,
                    "batch_id": p.batch_id,
                    "row_number": p.row_number,
                    "break_before": breaks.get(p.day),
                }
                for p in points
            ],
        }
        return respond(request, data, meta)

    @router.get("/instruments/{instrument_id}/indicators")
    def indicators(
        instrument_id: UUID,
        source_id: UUID,
        basis: Basis,
        indicator: Literal["SMA", "EMA", "RSI"],
        n: Annotated[int, Query(ge=1, le=MAX_POINTS)],
        request: Request,
        db: DB,
        start: date | None = None,
        end: date | None = None,
        assessment_as_of: datetime | None = None,
    ):
        validate_range(start, end)
        if indicator == "RSI" and n < 2:
            raise APIError(
                422,
                "INVALID_INDICATOR_PARAMETERS",
                "Wilder RSI requires an explicit integer n greater than 1.",
            )
        instrument, source = series(db, instrument_id, source_id)
        points = bounded_points(db, instrument_id, source_id, basis, end=end)
        meta = series_meta(db, instrument, source, basis, start, end, assessment_as_of)
        breaks = breaks_for(points, source.profile)
        reason = "BASIS_UNVERIFIED" if basis == "UNKNOWN" else None
        try:
            values = indicator_values(points, indicator, n, breaks) if not reason else []
        except DecimalException:
            reason, values = "NUMERIC_UNSUPPORTED", []
        if reason:
            values = [
                {
                    "trading_date": p.day,
                    "value": None,
                    "reason": reason,
                    "seed_date": None,
                    "break_before": breaks.get(p.day),
                }
                for p in points
            ]
        selected = [value for value in values if start is None or value["trading_date"] >= start]
        seeds = sorted({v["seed_date"] for v in values if v["seed_date"] is not None})
        any_value = any(v["value"] is not None for v in selected)
        unavailable = reason or (
            None
            if any_value
            else "NO_HISTORY"
            if not selected
            else "FLAT_WINDOW"
            if any(v["reason"] == "FLAT_WINDOW" for v in selected)
            else "INSUFFICIENT_HISTORY"
        )
        data = {
            "status": "AVAILABLE" if any_value else "UNAVAILABLE",
            "unavailable_reason": unavailable,
            "indicator_id": indicator,
            "algorithm_version": ALGORITHM_VERSION,
            "n": n,
            "window_unit": "OBSERVED_BARS",
            "series_ref": meta["series_ref"],
            "seed_date": seeds[0] if seeds else None,
            "seed_dates": seeds,
            "computed_at": now(),
            "input_evidence": evidence(points),
            "input_fingerprint": digest(
                {
                    "algorithm": ALGORITHM_VERSION,
                    "indicator": indicator,
                    "n": n,
                    "series": meta["series_ref"],
                    "points": input_identity(points),
                    "breaks": {d.isoformat(): r for d, r in breaks.items()},
                }
            ),
            "values": selected,
        }
        if reason:
            raise APIError(
                422, reason, "Derived values are unavailable for this input.", extra={"data": data}
            )
        return respond(request, data, meta)

    @router.post("/comparisons")
    def comparisons(body: ComparisonRequest, request: Request, db: DB):
        inputs, metadata = [], []
        assessment = body.assessment_as_of or now()
        for selection in body.series:
            instrument, source = series(db, selection.instrument_id, selection.source_id)
            points = bounded_points(
                db, instrument.id, source.id, selection.price_basis, body.start, body.end
            )
            meta = series_meta(
                db, instrument, source, selection.price_basis, body.start, body.end, assessment
            )
            inputs.append(
                ResearchSeries(
                    str(instrument.id),
                    instrument.currency,
                    selection.price_basis,
                    source.profile["data_class"],
                    source.profile.get("adjustment_definition_ref"),
                    points,
                )
            )
            meta.update(
                instrument={
                    "id": str(instrument.id),
                    "symbol": instrument.symbol,
                    "name": instrument.name,
                    "metal": instrument.metal,
                }
            )
            meta["input_fingerprint"] = digest(
                {
                    "method": METHOD_VERSION,
                    "series": meta["series_ref"],
                    "start": body.start,
                    "end": body.end,
                    "points": input_identity(points),
                }
            )
            metadata.append(meta)
        try:
            data = compare_series(inputs, body.start, body.end)
        except DecimalException:
            raise APIError(
                422, "NUMERIC_UNSUPPORTED", "Price comparison is unavailable for this input."
            ) from None
        data.update(
            computed_at=now(),
            input_fingerprint=digest(
                {
                    "method": METHOD_VERSION,
                    "start": body.start,
                    "end": body.end,
                    "inputs": [m["input_fingerprint"] for m in metadata],
                }
            ),
            limitations=[
                "PRICE_ONLY_NOT_TOTAL_RETURN",
                "NO_INFERRED_DISTRIBUTIONS_OR_ADJUSTMENTS",
                "NO_FUTURE_PERFORMANCE_INFERENCE",
                "UNVERIFIED_FOR_REPLAY",
            ],
        )
        for entry, meta in zip(data["series"], metadata):
            entry.update(meta=meta, input_fingerprint=meta["input_fingerprint"])
        if data["unavailable_reason"] not in {None, "NO_COMMON_DATES", "INSUFFICIENT_COMMON_DATES"}:
            raise APIError(
                422,
                data["unavailable_reason"],
                "Series comparison prerequisites are not established.",
                extra={"data": data},
            )
        return respond(request, data, {"assessment_as_of": assessment})
