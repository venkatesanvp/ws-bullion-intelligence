"""Authenticated P0 local market-research APIs; no provider secrets on the wire."""

import asyncio
from threading import Event
from datetime import date
from typing import Annotated, Literal
from uuid import UUID
from fastapi import Request
from pydantic import Field
from starlette.concurrency import run_in_threadpool
from .schemas import Strict


class QuoteRequest(Strict):
    refresh: bool = False


class IntradayRequest(Strict):
    instrument_id: UUID
    interval: int = Field(default=5, strict=True)
    preset: Literal["current", "previous", "five", "thirty", "custom"] = "current"
    start: date | None = None
    end: date | None = None
    indicators: dict[
        Literal["SMA", "EMA", "RSI"], Annotated[int, Field(strict=True, ge=1, le=10000)]
    ] = Field(default_factory=dict, max_length=3)
    refresh: bool = False


def register_session_market(router, respond):
    @router.get("/market-data/session-policy")
    def policy(request: Request):
        return respond(request, request.app.state.market_session.policy())

    @router.get("/market-data/session-diagnostics")
    def diagnostics(request: Request):
        service = request.app.state.market_session
        return respond(
            request,
            {
                "policy": service.policy(),
                "receipts": service.receipts,
                "retained_quotes": len(service.quotes),
                "retained_intraday_candles": sum(len(rows) for rows in service.candles.values()),
            },
        )

    @router.post("/market-data/quotes")
    def quotes(body: QuoteRequest, request: Request):
        return respond(request, request.app.state.market_session.get_quotes(refresh=body.refresh))

    @router.post("/market-data/intraday")
    async def intraday(body: IntradayRequest, request: Request):
        cancel = Event()
        task = asyncio.create_task(
            run_in_threadpool(
                request.app.state.market_session.intraday,
                body.instrument_id,
                body.interval,
                body.preset,
                body.start,
                body.end,
                indicators=body.indicators,
                refresh=body.refresh,
                cancel=cancel,
            )
        )
        try:
            while not task.done():
                if await request.is_disconnected():
                    cancel.set()
                await asyncio.sleep(0.05)
            return respond(request, await task)
        finally:
            cancel.set()
