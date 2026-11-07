"""Local bearer-authenticated SSE. No browser provider URL or provider credential.

Each viewer receives a coalesced latest snapshot at most once/second (no queued
raw ticks). Max 16 viewers. Application heartbeats are independent of trade age.
"""

import asyncio
import json
from datetime import date
from typing import Literal
from uuid import UUID
from fastapi import Request
from pydantic import Field
from starlette.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool
from .errors import APIError
from .schemas import Strict
from .serialization import plain


class StreamControl(Strict):
    action: Literal["connect", "disconnect"]


class ReconcileRequest(Strict):
    instrument_id: UUID
    session_date: date
    interval: int = Field(default=5, strict=True)


def register_market_stream(router, respond):
    @router.get("/market-data/stream-status")
    def status(request: Request):
        return respond(request, request.app.state.market_stream.status())

    @router.post("/market-data/stream-control")
    def control(body: StreamControl, request: Request):
        stream = request.app.state.market_stream
        return respond(
            request, stream.start(manual=True) if body.action == "connect" else stream.stop()
        )

    @router.get("/market-data/stream-events")
    async def events(request: Request):
        if request.headers.get("origin") not in request.app.state.settings.origins:
            raise APIError(
                403, "ORIGIN_REQUIRED", "A configured local Origin is required for streaming."
            )
        stream = request.app.state.market_stream
        stream.attach()

        async def generate():
            try:
                while not await request.is_disconnected():

                    def snapshot():
                        stream.start()
                        return {
                            "stream": stream.status(),
                            "quotes": request.app.state.market_session.get_quotes(cached_only=True),
                            "reconciliation_revision": request.app.state.market_reconciliation.revision,
                        }

                    # Lock contention with a bounded REST request must not block ASGI.
                    payload = await run_in_threadpool(snapshot)
                    yield "data: " + json.dumps(plain(payload), separators=(",", ":")) + "\n\n"
                    await asyncio.sleep(1)
            finally:
                stream.detach()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    @router.get("/market-data/reconciliation")
    def reconciliation(request: Request):
        return respond(request, request.app.state.market_reconciliation.status())

    @router.post("/market-data/reconcile")
    async def reconcile(body: ReconcileRequest, request: Request):
        # One instrument/day; existing daily single-flight, budget and backoff apply.
        result = await run_in_threadpool(
            request.app.state.market_reconciliation.reconcile,
            body.instrument_id,
            body.session_date,
            body.interval,
        )
        return respond(request, result)
