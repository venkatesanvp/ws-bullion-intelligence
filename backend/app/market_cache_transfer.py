"""Authenticated bounded RAM-to-RAM deployment transfer; never a disk/SQL cache.

Only the empty replacement process can restore. Provider credentials are not part of
any payload. Original absent evidence is marked absent, never reconstructed.
"""

from copy import copy, deepcopy
from threading import RLock
from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal
from fastapi import Request
from pydantic import Field, TypeAdapter
from .schemas import Strict
from .errors import APIError
from .serialization import plain
from .market_session import MarketQuote, IntradayCandle, INTERVALS
from .dhan_market_provider import financial, integral, epoch_seconds
from .transient_handoff import Handoff, restore_canonical_view


class SessionTransfer(Strict):
    version: int = 1
    daily: Handoff
    quotes: list[dict] = Field(default_factory=list, max_length=100)
    candles: list[dict] = Field(default_factory=list, max_length=100000)
    quote_attempts: int = Field(default=0, ge=0, le=100000)
    intraday_attempts: int = Field(default=0, ge=0, le=100000)
    daily_attempts: int = Field(default=0, ge=0, le=100000)
    budget_day: date | None = None
    budget_attempts: int | None = Field(default=None, ge=0, le=100000, strict=True)


def export_cache(app):
    service = app.state.market_session
    store = app.state.transient_research
    with service._quote_lock, service._intraday_lock, store._lock:
        series = []
        fields = (
            "id",
            "batch_id",
            "row_number",
            "trading_date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "ingested_at",
            "event_time",
            "event_precision",
            "provider_published_at",
        )
        for (iid, sid), data in store._datasets.items():
            evidence = list(data.get("handoff_evidence", ()))
            evidence.extend(p["summary"]["provenance"] for p in data.get("provenance", ()))
            if data.get("collected"):
                evidence.extend(
                    asdict(c.provenance) for c in data["collected"].chunks if c.provenance
                )
            observation_evidence = list(data.get("restored_observation_evidence", ()))
            observation_evidence.extend(
                e
                for record in data.get("provenance", ())
                for e in record.get("observation_provenance", ())
            )
            series.append(
                {
                    "instrument_id": iid,
                    "source_id": sid,
                    "isin": data["instrument"].isin,
                    "rows": [{k: getattr(r, k) for k in fields} for r in data["rows"]],
                    "batch_evidence": evidence[:2048],
                    "canonical_view_only": True,
                    "observation_evidence": [asdict(e) for e in observation_evidence],
                }
            )
        return plain(
            {
                "version": 1,
                "daily": {"series": series},
                "quotes": [asdict(q) for q in service.quotes.values()],
                "candles": [asdict(r) for rows in service.candles.values() for r in rows.values()],
                "quote_attempts": service.quote_attempts,
                "intraday_attempts": service.intraday_attempts,
                "daily_attempts": app.state.market_data.attempted_requests,
                "budget_day": service.budget.day,
                "budget_attempts": service.budget.attempts,
            }
        )


def restore_cache(app, body):
    service = app.state.market_session
    store = app.state.transient_research
    if body.version != 1:
        raise APIError(422, "INVALID_CACHE_TRANSFER", "Unsupported cache transfer version.")
    known = set(service.provider.listings())
    quotes = []
    candles = []
    try:
        for record in body.quotes:
            if any(
                v is not None and not isinstance(v, str)
                for k, v in record.items()
                if k in {"last_price", "open", "high", "low", "previous_close", "provider_close"}
            ):
                raise ValueError()
            row = TypeAdapter(MarketQuote).validate_python(record)
            if row.listing not in known or row.classification not in {"LIVE_QUOTE", "LIVE_STREAM"}:
                raise ValueError()
            for name in ("last_price", "open", "high", "low", "previous_close", "provider_close"):
                value = getattr(row, name)
                if value is not None:
                    financial(value)
            if row.volume is not None:
                integral(record["volume"])
            if (
                row.retrieved_at.tzinfo is None
                or row.last_trade_at
                and row.last_trade_at.tzinfo is None
            ):
                raise ValueError()
            quotes.append(row)
        for record in body.candles:
            if any(not isinstance(record.get(k), str) for k in ("open", "high", "low", "close")):
                raise ValueError()
            row = TypeAdapter(IntradayCandle).validate_python(record)
            for key in ("open", "high", "low", "close"):
                financial(getattr(row, key))
            integral(record["volume"])
            if (
                row.listing not in known
                or row.interval not in INTERVALS
                or row.start.tzinfo is None
                or row.end.tzinfo is None
                or row.retrieved_at.tzinfo is None
                or epoch_seconds(Decimal(row.source_timestamp)) != row.start
                or not row.start < row.end
                or row.end - row.start > timedelta(minutes=row.interval)
                or not row.low <= row.open <= row.high
                or not row.low <= row.close <= row.high
                or row.classification not in {"INTRADAY_COMPLETED", "INTRADAY_PROVISIONAL"}
            ):
                raise ValueError()
            candles.append(row)
    except Exception:
        raise APIError(
            422, "INVALID_CACHE_TRANSFER", "Canonical cache transfer validation failed."
        ) from None
    if len(candles) > service.settings.market_session_max_rows:
        raise APIError(422, "MEMORY_LIMIT", "Intraday transfer exceeds configured capacity.")
    if len({q.listing.isin for q in quotes}) != len(quotes) or len(
        {(r.listing.isin, r.interval, r.start) for r in candles}
    ) != len(candles):
        raise APIError(422, "INVALID_CACHE_TRANSFER", "Duplicate cache identities rejected.")
    with service._quote_lock, service._intraday_lock, store._lock:
        if service.quotes or service.candles or service.quote_attempts or service.intraday_attempts:
            raise APIError(409, "HANDOFF_CLOSED", "Restore before any quote/intraday acquisition.")
        # Stage the whole handoff in a private store. No live publication before
        # daily validation AND intraday coverage calculation have both succeeded.
        shadow = copy(store)
        shadow._lock = RLock()
        shadow._datasets = {
            key: {**data, "instrument": deepcopy(data["instrument"]), "source": deepcopy(data["source"])}
            for key, data in store._datasets.items()
        }
        body = body.model_copy(deep=True)
        # Remap ephemeral catalog IDs by verified ISIN; keep observation/batch IDs.
        for series in body.daily.series:
            target = next((i for i in store.listings() if i.isin == series.isin), None)
            if target is None:
                raise APIError(422, "INVALID_CACHE_TRANSFER", "Unknown daily identity.")
            source = store.sources()[0]
            series.instrument_id = target.id
            series.source_id = source.id
        restored = restore_canonical_view(shadow, body.daily, service.settings.market_data_max_rows)
        staged_candles, staged_revisions, staged_coverage = {}, {}, {}
        for row in candles:
            key = (row.listing.isin, row.interval)
            staged_candles.setdefault(key, {})[row.start] = row
            staged_revisions[key] = 1
        for key, rows in staged_candles.items():
            for day in {r.start.date() for r in rows.values()}:
                expected = service.expected_starts(day, key[1], service.clock())
                complete = expected is not None and set(expected) <= {
                    r.start for r in rows.values()
                }
                stamp = max(r.retrieved_at for r in rows.values() if r.start.date() == day)
                staged_coverage[(key, day)] = (stamp, "COMPLETE" if complete else "PARTIAL")
        # Publish only fully prepared state. A disconnected caller can safely
        # inspect/export and compare; replay remains fail-closed (409), never merges.
        store._datasets = shadow._datasets
        store._handoff_sealed = True
        service.quotes = {q.listing.isin: q for q in quotes}
        service.quote_checked = max((q.retrieved_at for q in quotes), default=None)
        service.quote_generation = 1 if quotes else 0
        service.candles = staged_candles
        service.revisions = staged_revisions
        service.coverage = staged_coverage
        service.quote_attempts = body.quote_attempts
        service.intraday_attempts = body.intraday_attempts
        app.state.market_data.attempted_requests = body.daily_attempts
        # Daily budget is separate from lifetime per-capability counters.
        # Legacy payloads remain conservative, but do not provide exact daily evidence.
        service.budget.attempts = (
            body.budget_attempts if body.budget_attempts is not None
            else body.quote_attempts + body.intraday_attempts + body.daily_attempts
        )
        service.budget.day = body.budget_day if body.budget_attempts is not None else service.clock().date()
        return {
            "daily_observations": restored["observations"],
            "quotes": len(quotes),
            "intraday_candles": len(candles),
            "persistence": "NONE",
        }


def register_cache_transfer(router, respond):
    @router.get("/market-data/cache-transfer")
    def export(request: Request):
        return respond(request, export_cache(request.app))

    @router.post("/market-data/cache-transfer")
    def restore(body: SessionTransfer, request: Request):
        if not request.app.state.settings.market_data_enabled:
            raise APIError(403, "MARKET_DATA_DISABLED", "Live operating policy is disabled.")
        return respond(request, restore_cache(request.app, body))
