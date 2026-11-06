"""One-time authenticated canonical RAM-view handoff for this deployment.

Not a provider-response importer. Reuses canonical numeric guards, preserves existing
observation/batch IDs and exposed batch provenance. Original numeric provider epochs
were not exposed by the old API; they remain explicitly unavailable for migrated rows.
No file/SQL I/O, no credentials, and no calls to the provider.
"""

from dataclasses import asdict
from datetime import date, datetime, timezone
from uuid import UUID
from fastapi import Request
from pydantic import Field, field_validator
from .daily_values import price
from .errors import APIError
from .market_data import BatchProvenance, DailyObservation
from .models import Observation
from .schemas import Strict


class CanonicalView(Strict):
    id: UUID
    batch_id: UUID
    row_number: int = Field(ge=1)
    trading_date: date
    open: str = Field(max_length=128)
    high: str = Field(max_length=128)
    low: str = Field(max_length=128)
    close: str = Field(max_length=128)
    volume: int = Field(ge=0, le=2**63 - 1, strict=True)
    ingested_at: datetime
    event_time: None = None
    event_precision: str = "SESSION_DATE"
    provider_published_at: None = None

    @field_validator("ingested_at")
    @classmethod
    def aware(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timezone required")
        return value


class HandoffSeries(Strict):
    instrument_id: UUID
    source_id: UUID
    isin: str = Field(pattern=r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")
    rows: list[CanonicalView] = Field(max_length=100000)
    batch_evidence: list[BatchProvenance] = Field(max_length=2048)


class Handoff(Strict):
    series: list[HandoffSeries] = Field(min_length=1, max_length=100)


def restore_canonical_view(store, body, max_rows):
    """Publish an entirely validated snapshot once; no partially restored publication."""
    with store._lock:
        if getattr(store, "_handoff_sealed", False) or any(
            d["rows"] for d in store._datasets.values()
        ):
            raise APIError(
                409, "HANDOFF_CLOSED", "RAM handoff is available only once before acquisition."
            )
        if sum(len(s.rows) for s in body.series) > max_rows:
            raise APIError(422, "MEMORY_LIMIT", "Handoff exceeds transient capacity.")
        replacements, seen_keys, seen_ids = {}, set(), set()
        for item in body.series:
            key = (item.instrument_id, item.source_id)
            if key in seen_keys or key not in store._datasets:
                raise APIError(422, "INVALID_HANDOFF", "Handoff must match configured listings.")
            seen_keys.add(key)
            data = store._datasets[key]
            instrument = data["instrument"]
            if instrument.isin != item.isin or any(
                (b.listing.isin, b.listing.symbol, b.listing.exchange)
                != (instrument.isin, instrument.symbol, instrument.exchange)
                or b.provider != "DHANHQ"
                or b.timestamp_semantics_verified
                for b in item.batch_evidence
            ):
                raise APIError(
                    422, "INVALID_HANDOFF", "Handoff identity/provisional evidence mismatch."
                )
            if item.rows and not item.batch_evidence:
                raise APIError(422, "INVALID_HANDOFF", "Original batch evidence is required.")
            rows, days = [], set()
            for row in item.rows:
                try:
                    values = {
                        name: price(getattr(row, name)) for name in ("open", "high", "low", "close")
                    }
                    if (
                        row.id in seen_ids
                        or row.trading_date in days
                        or not date(2000, 1, 1) <= row.trading_date < date(2100, 1, 1)
                        or row.trading_date > datetime.now(timezone.utc).date()
                        or row.event_precision != "SESSION_DATE"
                        or not values["low"] <= values["open"] <= values["high"]
                        or not values["low"] <= values["close"] <= values["high"]
                        or not any(
                            b.requested_start <= row.trading_date <= b.requested_end
                            for b in item.batch_evidence
                        )
                    ):
                        raise ValueError()
                    seen_ids.add(row.id)
                    days.add(row.trading_date)
                    candidate = DailyObservation(
                        row.trading_date, **values, volume=row.volume, provenance=None
                    )
                    rows.append(
                        Observation(
                            id=row.id,
                            instrument_id=instrument.id,
                            source_id=item.source_id,
                            batch_id=row.batch_id,
                            row_number=row.row_number,
                            canonical_hash=candidate.canonical_hash,
                            ingested_at=row.ingested_at,
                            **candidate.canonical_values(),
                        )
                    )
                except (ValueError, ArithmeticError, TypeError):
                    raise APIError(
                        422, "INVALID_HANDOFF", "Canonical handoff validation failed."
                    ) from None
            replacements[key] = {
                **data,
                "rows": tuple(sorted(rows, key=lambda r: r.trading_date)),
                "handoff_evidence": tuple(asdict(b) for b in item.batch_evidence),
                "source_epoch_evidence": "NOT_EXPOSED_BY_LEGACY_CANONICAL_VIEW",
            }
            # The old read model exposes all canonical values and IDs, not raw provider epochs.
        for key, data in replacements.items():
            data["source"].profile = {
                **data["source"].profile,
                "handoff_limitation": "ORIGINAL_NUMERIC_EPOCH_NOT_EXPORTED",
            }
            data["instrument"].data_revision = 1 if data["rows"] else 0
        store._datasets = {**store._datasets, **replacements}
        store._handoff_sealed = True
        return {
            "status": "RESTORED_CANONICAL_VIEW",
            "observations": sum(len(v["rows"]) for v in replacements.values()),
            "source_epoch_evidence": "NOT_EXPOSED_BY_LEGACY_CANONICAL_VIEW",
            "persistence": "NONE",
        }


def register_handoff(router, respond):
    @router.post("/market-data/handoff")
    def handoff(body: Handoff, request: Request):
        if not request.app.state.settings.market_data_enabled:
            raise APIError(
                403, "MARKET_DATA_DISABLED", "Enable the read-only operating policy first."
            )
        result = restore_canonical_view(
            request.app.state.transient_research,
            body,
            request.app.state.settings.market_data_max_rows,
        )
        return respond(request, result)
