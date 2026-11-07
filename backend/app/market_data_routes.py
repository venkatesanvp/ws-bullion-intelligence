"""Authenticated local market-data orchestration; sanitized status only."""

import asyncio
from threading import Event
from datetime import date
from uuid import UUID
from fastapi import Request
from pydantic import Field
from starlette.concurrency import run_in_threadpool
from .schemas import Strict


class EnsureHistory(Strict):
    instrument_id: UUID
    source_id: UUID
    start: date | None = None
    end: date | None = None
    warmup_bars: int = Field(default=0, ge=0, le=10000)
    refresh: bool = False


def register_market_data(router, respond):
    @router.get("/market-data/policy")
    def policy(request: Request):
        return respond(request, request.app.state.market_data.public_policy())

    @router.post("/market-data/ensure")
    async def ensure(body: EnsureHistory, request: Request):
        cancel = Event()
        task = asyncio.create_task(
            run_in_threadpool(
                request.app.state.market_data.ensure,
                body.instrument_id,
                body.source_id,
                body.start,
                body.end,
                warmup_bars=body.warmup_bars,
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
