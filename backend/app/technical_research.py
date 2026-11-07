"""Snapshot-consistent, read-only Package 2 daily OHLCV/technical research."""

from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID
from decimal import DecimalException
from fastapi import Depends, Request
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .schemas import Strict
from .analytics import MAX_POINTS, Point, indicator_values
from .technical_analytics import TechnicalParameters, CandlePoint, technical_values
from .market_session import IST
from .models import Observation, now
from .queries import series, series_meta
from .research import breaks_for, validate_range
from .serialization import digest
from .errors import APIError


class TechnicalRequest(Strict):
    instrument_id: UUID
    source_id: UUID
    basis: Literal["RAW_CLOSE", "PROVIDER_ADJUSTED", "UNKNOWN"]
    start: date | None = None
    end: date | None = None
    parameters: TechnicalParameters = Field(default_factory=TechnicalParameters)


def register_technical_research(router, get_db, respond):
    DB = Annotated[Session, Depends(get_db)]

    @router.post("/research/technical")
    def technical(body: TechnicalRequest, request: Request, db: DB):
        validate_range(body.start, body.end)
        if body.basis == "UNKNOWN":
            raise APIError(
                422, "BASIS_UNVERIFIED", "Technical research requires an explicit price basis."
            )
        instrument, source = series(db, body.instrument_id, body.source_id)
        memory = db.info.get("transient_research")
        if memory and memory.has_series(instrument.id, source.id):
            rows = memory.rows(instrument.id, source.id, body.basis, end=body.end)
        else:
            query = select(Observation).where(
                Observation.instrument_id == instrument.id,
                Observation.source_id == source.id,
                Observation.price_basis == body.basis,
                Observation.interval == "1d",
            )
            if body.end:
                query = query.where(Observation.trading_date <= body.end)
            rows = tuple(
                db.scalars(
                    query.order_by(Observation.trading_date, Observation.id).limit(MAX_POINTS + 1)
                )
            )
        if len(rows) > MAX_POINTS:
            raise APIError(
                422,
                "ANALYTICS_RANGE_LIMIT",
                "Complete technical prefix exceeds 10000 rows; no prefix was truncated.",
            )
        today = datetime.now(IST).date()
        excluded = sum(r.trading_date >= today for r in rows)
        rows = tuple(
            r for r in rows if r.trading_date < today
        )  # Conservative daily publication guard.
        points = [
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
        breaks = breaks_for(points, source.profile)
        candles = [
            CandlePoint(r.trading_date, r.close, r.open, r.high, r.low, r.volume) for r in rows
        ]
        p = body.parameters
        try:
            calculated = technical_values(candles, p, breaks)
            for name, n in (("SMA", p.sma_n), ("EMA", p.ema_n), ("RSI", p.rsi_n)):
                calculated[name] = {
                    "algorithm_version": "decimal-research-v1",
                    "n": n,
                    "values": [
                        {
                            "time": v["trading_date"],
                            **{k: x for k, x in v.items() if k != "trading_date"},
                        }
                        for v in indicator_values(points, name, n, breaks)
                    ],
                }
        except (ValueError, DecimalException):
            raise APIError(
                422, "NUMERIC_UNSUPPORTED", "Technical values cannot be calculated for this input."
            ) from None
        for value in calculated.values():
            value["values"] = [
                v for v in value["values"] if body.start is None or v["time"] >= body.start
            ]
        selected = [r for r in rows if body.start is None or r.trading_date >= body.start]
        meta = series_meta(db, instrument, source, body.basis, body.start, body.end)
        result = {
            "instrument_id": str(instrument.id),
            "symbol": instrument.symbol,
            "timeframe": "1d",
            "parameters": p.model_dump(),
            "indicators": calculated,
            "gap_times": [
                str(d)
                for d in (source.profile.get("calendar") or {}).get("session_dates", [])
                if selected
                and str(selected[0].trading_date) <= str(d) <= str(selected[-1].trading_date)
                and str(d) not in {str(r.trading_date) for r in selected}
            ][:1000],
            "candles": [
                {
                    "time": r.trading_date,
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": str(r.volume) if r.volume is not None else None,
                    "observation_id": str(r.id),
                    "batch_id": str(r.batch_id),
                    "canonical_hash": r.canonical_hash,
                    "classification": "HISTORICAL_FINAL",
                    "break_before": breaks.get(r.trading_date),
                }
                for r in selected
            ],
            "status": "AVAILABLE" if selected else "UNAVAILABLE",
            "series_ref": meta["series_ref"],
            "input_fingerprint": digest(
                {
                    "series_ref": meta["series_ref"],
                    "rows": [(str(r.id), r.canonical_hash) for r in rows],
                    "parameters": p.model_dump(),
                    "breaks": {str(k): v for k, v in breaks.items()},
                    "range": (body.start, body.end),
                }
            ),
            "computed_at": now(),
            "warmup_bars": sum(
                body.start is not None and r.trading_date < body.start for r in rows
            ),
            "excluded_incomplete_daily_rows": excluded,
            "source": source.label,
            "source_qualification": source.qualification,
            "price_basis": body.basis,
            "freshness": meta["freshness"]["status"],
            "exchange_timezone": "Asia/Kolkata",
            "warnings": [
                "FINALITY_IS_NOT_SOURCE_QUALIFICATION",
                "CURRENT_FUTURE_DAILY_ROWS_EXCLUDED",
                "NO_FORECAST_OR_TRADING_SIGNAL",
                "PRICE_ADJUSTMENT_AND_REPLAY_QUALIFICATION_REQUIRED",
            ],
        }
        return respond(request, result, meta)
