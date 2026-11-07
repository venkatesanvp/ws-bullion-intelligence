"""Transient reconciliation of validated provider daily and intraday candidates.

Never constructs history from quotes/ticks. Existing daily acquisition validates
and publishes atomically; differing history requires its explicit refresh pathway.
HISTORICAL_FINAL describes provider finality, not full source qualification.
"""

from threading import RLock
from .errors import APIError
from .market_session import regular_bounds
from .serialization import digest


class MarketReconciliation:
    def __init__(self, session):
        self.session = session
        self._lock = RLock()
        self.records = {}
        self.audit = []
        self.revision = 0

    def status(self):
        with self._lock:
            return {
                "revision": self.revision,
                "records": list(self.records.values()),
                "audit": self.audit[-100:],
                "retention": "PROCESS_MEMORY_ONLY",
                "source_qualification": "TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED",
                "difference_policy": "ANY_NONZERO_FIELD_DIFFERENCE_REQUIRES_REVIEW",
                "adjustment_compatibility": "UNQUALIFIED",
            }

    def reconcile(self, instrument_id, day, interval=5, *, cancel=None):
        instrument, listing = self.session.resolve(instrument_id)
        daily = self.session.daily
        if interval not in (1, 5, 15, 25, 60) or type(interval) is not int:
            raise APIError(422, "INVALID_INTERVAL", "Use a documented intraday interval.")
        if not self.session.settings.market_data_enabled:
            raise APIError(409, "MARKET_DATA_DISABLED", "Market data is disabled.")
        if daily.session(day) is not True:
            raise APIError(422, "CALENDAR_UNASSESSED", "Select a reviewed trading session.")
        source = next(
            (s for s in daily.store.sources() if daily.store.has_series(instrument.id, s.id)), None
        )
        if source is None:
            raise APIError(422, "UNVERIFIED_SOURCE", "Configured transient source required.")
        _, eligible = daily.limits()
        acquisition = None
        if day <= eligible:
            acquisition = daily.ensure(instrument.id, source.id, day, day, cancel=cancel)
        store = daily.store.snapshot()
        official = next(
            iter(store.rows(instrument.id, source.id, "PROVIDER_ADJUSTED", day, day)), None
        )
        with self.session._intraday_lock:
            bars = sorted(
                (
                    r
                    for r in self.session.candles.get((listing.isin, interval), {}).values()
                    if r.start.date() == day
                ),
                key=lambda r: r.start,
            )
        expected = self.session.expected_starts(day, interval, self.session.clock())
        opening, closing = regular_bounds(day)
        full = bool(
            bars
            and expected is not None
            and bars[0].start == opening
            and bars[-1].end == closing
            and all(b.classification == "INTRADAY_COMPLETED" for b in bars)
            and all(a.end == b.start for a, b in zip(bars, bars[1:]))
            and len({b.start for b in bars}) == len(bars)
        )
        aggregate = None
        if bars:
            aggregate = dict(
                open=bars[0].open,
                high=max(r.high for r in bars),
                low=min(r.low for r in bars),
                close=bars[-1].close,
                volume=sum(r.volume for r in bars)
                if all(r.volume_semantics == "PER_CANDLE_VOLUME" for r in bars)
                else None,
            )
        differences = []
        if official and aggregate:
            differences = [
                k
                for k, v in aggregate.items()
                if v is not None and getattr(official, k) is not None and v != getattr(official, k)
            ]
        result = {
            "instrument_id": str(instrument.id),
            "symbol": listing.symbol,
            "session_date": day,
            "interval_minutes": interval,
            "classification": "HISTORICAL_FINAL"
            if official
            else "INTRADAY_PROVISIONAL"
            if bars
            else "UNAVAILABLE",
            "provisional_disposition": "SUPERSEDED_BY_VALIDATED_PROVIDER_DAILY"
            if official and bars
            else "RETAINED_SEPARATELY"
            if bars
            else "NOT_AVAILABLE",
            "provisional_coverage": "COMPLETE_REGULAR_SESSION"
            if full
            else "PARTIAL"
            if bars
            else "UNAVAILABLE",
            "provisional_bar_count": len(bars),
            "differing_fields": differences,
            "comparison_status": "REVIEW_DIFFERENCES"
            if differences
            else "MATCHING_FIELDS_UNQUALIFIED_BASIS"
            if official and full
            else "INSUFFICIENT_COMPARABLE_COVERAGE",
            "official_observation_id": str(official.id) if official else None,
            "official_batch_id": str(official.batch_id) if official else None,
            "official_hash": official.canonical_hash if official else None,
            "official_ingested_at": official.ingested_at if official else None,
            "provisional_hash": digest(aggregate) if aggregate else None,
            "latest_provider_timestamp": bars[-1].start if bars else None,
            "last_intraday_retrieval": max((r.retrieved_at for r in bars), default=None),
            "publication_state": "AVAILABLE"
            if official
            else "WAITING_T_MINUS_ONE"
            if day > eligible
            else "NOT_YET_PUBLISHED_OR_UNAVAILABLE",
            "requests": acquisition["requests"] if acquisition else 0,
            "error": acquisition.get("error") if acquisition else None,
            "source_qualification": source.qualification,
            "price_basis": "PROVIDER_ADJUSTED_DAILY_VS_UNQUALIFIED_INTRADAY",
            "warnings": [
                "FINALITY_IS_NOT_SOURCE_QUALIFICATION",
                "ADJUSTMENT_COMPATIBILITY_UNQUALIFIED",
                "VOLUME_SCOPE_AND_SPECIAL_SESSIONS_UNQUALIFIED",
                "NO_TOTAL_RETURN_CLAIM",
            ],
        }
        key = (listing.isin, day, interval)
        with self._lock:
            old = self.records.get(key)
            if old != result:
                if len(self.records) >= 1000 and key not in self.records:
                    raise APIError(
                        409,
                        "RECONCILIATION_MEMORY_LIMIT",
                        "Reconciliation metadata capacity reached.",
                    )
                self.revision += 1
                self.records[key] = result
                self.audit = (
                    self.audit
                    + [
                        {
                            "revision": self.revision,
                            "symbol": listing.symbol,
                            "session_date": day,
                            "previous_record_hash": digest(old) if old else None,
                            "record_hash": digest(result),
                            "differing_fields": differences,
                            "recorded_at": self.session.clock(),
                        }
                    ]
                )[-1000:]
        return result

    def superseded(self, instrument_id, day):
        with self._lock:
            return any(
                r["instrument_id"] == str(instrument_id)
                and r["session_date"] == day
                and r["classification"] == "HISTORICAL_FINAL"
                for r in self.records.values()
            )
