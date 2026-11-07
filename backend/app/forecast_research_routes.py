"""Authenticated read-only computation routes; no token/provider acquisition methods."""

import asyncio
from threading import Event
from typing import Annotated
from uuid import UUID
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from .models import Observation
from .queries import series
from .errors import APIError
from .forecast_contracts import ForecastError
from .forecast_research_service import ResearchOptions


def register_forecast_research(router, get_db, respond):
    DB = Annotated[Session, Depends(get_db)]

    def reader(request, db, body):
        def read():
            instrument, source = series(db, body.instrument_id, body.source_id)
            if not instrument.active:
                raise ForecastError("INSTRUMENT_INACTIVE")
            memory = db.info.get("transient_research")
            if memory and memory.has_series(instrument.id, source.id):
                rows = memory.rows(instrument.id, source.id, body.basis)
            else:
                rows = tuple(
                    db.scalars(
                        select(Observation)
                        .where(
                            Observation.instrument_id == instrument.id,
                            Observation.source_id == source.id,
                            Observation.price_basis == body.basis,
                            Observation.interval == "1d",
                        )
                        .order_by(Observation.trading_date, Observation.id)
                        .limit(5001)
                    )
                )
            return instrument, source, rows

        return read

    async def compute(action, body, request, db, run_id=None):
        cancel = Event()
        service = request.app.state.forecast_research
        task = asyncio.create_task(
            run_in_threadpool(
                service.work, action, reader(request, db, body), body, cancel, run_id=run_id
            )
        )
        try:
            while not task.done():
                if await request.is_disconnected():
                    cancel.set()
                await asyncio.sleep(0.05)
            return respond(request, await task)
        except ForecastError as exc:
            status = (
                404
                if exc.code == "TRACKING_NOT_FOUND_OR_EXPIRED"
                else 409
                if exc.code == "FORECAST_SOURCE_SNAPSHOT_CHANGED"
                else 429
                if exc.code in {"FORECAST_BUSY", "FORECAST_RATE_LIMITED"}
                else 408
                if exc.code in {"FORECAST_TIMEOUT", "FORECAST_CANCELLED"}
                else 422
            )
            raise APIError(
                status,
                exc.code,
                "Forecast research could not complete under the requested data, calendar or resource constraints.",
            ) from None
        finally:
            cancel.set()

    @router.get("/research/forecasts/context")
    async def context(
        request: Request,
        db: DB,
        instrument_id: UUID,
        source_id: UUID,
        basis: str = "PROVIDER_ADJUSTED",
    ):
        return await compute(
            "context",
            ResearchOptions(instrument_id=instrument_id, source_id=source_id, basis=basis),
            request,
            db,
        )

    @router.post("/research/forecasts/run")
    async def run(body: ResearchOptions, request: Request, db: DB):
        return await compute("run", body, request, db)

    @router.post("/research/forecasts/evaluate")
    async def historical(body: ResearchOptions, request: Request, db: DB):
        return await compute("evaluate", body, request, db)

    @router.get("/research/forecasts/performance")
    def performance_registry(request: Request):
        return respond(request, request.app.state.forecast_research.performance_registry())

    @router.get("/research/forecasts/runs")
    def receipts(request: Request):
        return respond(
            request,
            {
                "runs": request.app.state.forecast_research.receipts(),
                "retention": "PROCESS_SCOPED_MAX_32_TARGET_PLUS_7_DAYS_MAX_365",
            },
        )

    @router.get("/research/forecasts/runs/{run_id}")
    async def tracking(run_id: UUID, request: Request, db: DB):
        try:
            i, s = request.app.state.forecast_research.identifiers(run_id)
        except ForecastError:
            raise APIError(
                404,
                "TRACKING_NOT_FOUND_OR_EXPIRED",
                "The session-scoped forecast is absent or expired; backend restart loses tracking.",
            ) from None
        return await compute(
            "track", ResearchOptions(instrument_id=i, source_id=s), request, db, str(run_id)
        )
