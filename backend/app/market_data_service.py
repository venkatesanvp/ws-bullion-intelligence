"""Step 5D.4: provider-neutral bounded coverage/acquisition over the existing RAM sink.

No SQL writes, file cache, token exchange, account access or analytical formulas.
The composition root alone supplies the verified adapter/catalog and operating grant.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from threading import Event, Lock
import time

from .acquisition import CollectedSeries
from .errors import APIError
from .market_data import DailyRequest
from .serialization import digest

IST = timezone(timedelta(hours=5, minutes=30))
DAY = timedelta(days=1)


@dataclass(frozen=True)
class Coverage:
    state: str
    checked_at: datetime
    error: str | None = None


class MarketDataService:
    def __init__(
        self,
        provider,
        store,
        policy,
        calendar=None,
        *,
        availability=None,
        clock=None,
        monotonic=time.monotonic,
        budget=None,
    ):
        self.provider, self.store, self.policy, self.calendar = provider, store, policy, calendar
        self.availability = availability or {}  # verified ISIN -> inception date, never guessed
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.monotonic = monotonic
        self.budget = budget
        self._operation = Lock()  # Global single flight; replan after each waiter acquires.
        self._coverage = {}
        self._last_request = 0.0
        self._budget_day, self._daily_requests = None, 0
        self._provider_blocked_until = None
        self.attempted_requests = 0
        self._sessions = set(calendar.session_dates) if calendar else set()

    def session(self, day):
        if self.calendar and self.calendar.coverage_start <= day <= self.calendar.coverage_end:
            return day in self._sessions
        return None  # Outside reviewed calendar: even weekends remain unassessed.

    def limits(self):
        local = self.clock().astimezone(IST)
        # Conservative publication bound: daily data is documented as T-1, no precise SLA.
        eligible = local.date() - DAY
        completed = local.date() if local.hour >= 16 else eligible

        def last_session(day):
            while self.session(day) is False:
                day -= DAY
            return day

        return last_session(completed), last_session(eligible)

    def public_policy(self):
        completed, eligible = self.limits()
        return {
            "enabled": self.policy.market_data_enabled,
            "automatic_missing": self.policy.market_data_auto_missing,
            "max_requests_per_operation": self.policy.market_data_max_requests,
            "partition_days": self.policy.market_data_partition_days,
            "timeout_seconds": self.policy.market_data_timeout_seconds,
            "max_concurrent_provider_requests": 1,
            "auto_refresh_seconds": self.policy.market_data_auto_refresh_seconds,
            "latest_completed_session_candidate": completed.isoformat(),
            "latest_provider_eligible_session_candidate": eligible.isoformat(),
            "publication_policy": "T_MINUS_ONE_NO_PUBLICATION_SLA",
            "calendar_coverage_end": self.calendar.coverage_end.isoformat()
            if self.calendar
            else None,
            "retention": "PROCESS_MEMORY_ONLY_BOUNDED_NO_DISK_OR_SQL",
            "requests_attempted_this_process": self.attempted_requests,
            "source_qualified": False,
        }

    def _days(self, start, end):
        return (start + timedelta(days=n) for n in range((end - start).days + 1))

    def _states(self, key, listing, start, end, rows, now, eligible):
        available = {r.trading_date: r for r in rows}
        inception = self.availability.get(listing.isin)
        states = {}
        for day in self._days(start, end):
            if day in available:
                checked = self._coverage.get((key, day))
                states[day] = Coverage(
                    "AVAILABLE", checked.checked_at if checked else available[day].ingested_at
                )
            elif inception and day < inception:
                states[day] = Coverage("OUTSIDE_VERIFIED_HISTORY", now)
            elif self.session(day) is False:
                states[day] = Coverage("NON_TRADING", now)
            elif day > eligible:
                states[day] = Coverage("PROVIDER_PENDING", now)
            else:
                states[day] = self._coverage.get((key, day), Coverage("NOT_REQUESTED", now))
        return states

    def ensure(
        self,
        instrument_id,
        source_id,
        start=None,
        end=None,
        *,
        warmup_bars=0,
        refresh=False,
        cancel=None,
    ):
        cancel = cancel or Event()
        if cancel.is_set():
            return {"status": "CANCELLED", "requests": 0, "error": None}
        started, waiting_since = self.clock(), self.monotonic()
        coalesced = not self._operation.acquire(blocking=False)
        while coalesced and not self._operation.acquire(timeout=0.1):
            if cancel.is_set():
                return {"status": "CANCELLED", "requests": 0, "error": None}
            if self.monotonic() - waiting_since > 180:
                return {"status": "BUSY", "requests": 0, "error": "ACQUISITION_BUSY"}
        try:
            return self._ensure(
                instrument_id,
                source_id,
                start,
                end,
                warmup_bars,
                refresh,
                cancel,
                started,
                coalesced,
            )
        finally:
            self._operation.release()

    def _ensure(
        self, instrument_id, source_id, start, end, warmup_bars, refresh, cancel, started, coalesced
    ):
        if not self.store.has_series(instrument_id, source_id):
            raise APIError(
                409,
                "NOT_TRANSIENT_PROVIDER_SERIES",
                "Select a configured transient provider source.",
            )
        instrument, source = self.store.series(instrument_id, source_id)
        listing = next(
            (
                x
                for x in self.provider.listings()
                if (x.exchange, x.symbol, x.isin, x.currency, x.metal)
                == (
                    instrument.exchange,
                    instrument.symbol,
                    instrument.isin,
                    instrument.currency,
                    instrument.metal,
                )
            ),
            None,
        )
        if listing is None:
            raise APIError(409, "UNVERIFIED_INSTRUMENT", "A verified provider mapping is required.")
        self.store._handoff_sealed = True
        now = self.clock()
        completed, eligible = self.limits()
        today = now.astimezone(IST).date()
        rows = self.store.rows(instrument_id, source_id, "PROVIDER_ADJUSTED")
        start = start or (rows[0].trading_date if rows else today - timedelta(days=365))
        end = end or today
        if not date(2000, 1, 1) <= start <= end < date(2100, 1, 1):
            raise APIError(422, "INVALID_DATE_RANGE", "Use an ordered supported historical range.")
        if (end - start).days > 7305:
            raise APIError(422, "RANGE_TOO_LARGE", "Select at most twenty years per operation.")
        visible_start = start
        if warmup_bars:
            # Retrieve a bounded deterministic prefix; never invent missing observations.
            prior = sorted((d for d in self._sessions if d < start), reverse=True)
            if len(prior) >= warmup_bars:
                start = prior[warmup_bars - 1]
            else:
                start = max(
                    date(2000, 1, 1), start - timedelta(days=min(20000, warmup_bars * 2 + 30))
                )
        key = (instrument_id, source_id)
        states = self._states(key, listing, start, end, rows, now, eligible)
        if (
            len(self._coverage) + sum((key, d) not in self._coverage for d in states)
            > self.policy.market_data_max_coverage_days
        ):
            raise APIError(
                409, "COVERAGE_MEMORY_LIMIT", "Coverage capacity reached; narrow the request."
            )
        need = []
        stale = set()
        for day, entry in states.items():
            age = max(0, (now - entry.checked_at).total_seconds())
            if day > eligible or entry.state in {"NON_TRADING", "OUTSIDE_VERIFIED_HISTORY"}:
                continue
            # Concurrent explicit refreshes reuse a just-completed refresh after waiting.
            force = refresh and (not coalesced or entry.checked_at < started)
            due = (
                entry.state == "NOT_REQUESTED"
                or force
                or entry.state == "AVAILABLE"
                and age >= self.policy.market_data_freshness_seconds
                or entry.state == "ATTEMPTED_EMPTY"
                and age >= self.policy.market_data_empty_retry_seconds
                or entry.state in {"FAILED", "REJECTED"}
                and age >= self.policy.market_data_failure_backoff_seconds
            )
            if due:
                need.append(day)
                if entry.state == "AVAILABLE":
                    stale.add(day)
        ranges = []
        for day in need:
            # Bridge only confirmed closures. Never re-download intervening available sessions.
            if (
                ranges
                and (day - ranges[-1][0]).days < self.policy.market_data_partition_days
                and all(
                    self.session(d) is False for d in self._days(ranges[-1][1] + DAY, day - DAY)
                )
            ):
                ranges[-1] = (ranges[-1][0], day)
            else:
                ranges.append((day, day))
        requests, added, revised, error, cancelled = 0, 0, 0, None, False
        if need and not self.policy.market_data_enabled:
            error = "MARKET_DATA_DISABLED"
        elif need and not refresh and not self.policy.market_data_auto_missing:
            error = "AUTOMATIC_RETRIEVAL_DISABLED"
        else:
            for left, right in ranges[: self.policy.market_data_max_requests]:
                if cancel.is_set():
                    cancelled = True
                    break
                now = self.clock()
                if self._provider_blocked_until and now < self._provider_blocked_until:
                    error = "PROVIDER_BACKOFF"
                    break
                budget_day = now.astimezone(IST).date()
                if budget_day != self._budget_day:
                    self._budget_day, self._daily_requests = budget_day, 0
                if self._daily_requests >= self.policy.market_data_daily_budget:
                    error = "LOCAL_DAILY_BUDGET"
                    break
                wait = self.policy.market_data_min_interval_seconds - (
                    self.monotonic() - self._last_request
                )
                if wait > 0 and cancel.wait(wait):
                    cancelled = True
                    break
                calendar = (
                    self.calendar
                    if self.calendar
                    and self.calendar.coverage_start <= left <= right <= self.calendar.coverage_end
                    else None
                )
                request = DailyRequest(listing, left, right, calendar)
                try:

                    def call():
                        return self.provider.retrieve_daily(request, request_approved=True)

                    result = self.budget.invoke(call, operation="DAILY_HISTORY", trigger="MANUAL_REFRESH" if refresh else "RANGE_ENSURE") if self.budget else call()
                except APIError as exc:
                    from .market_data import DailyResult, ProviderFailure

                    result = DailyResult("FAILED", failure=ProviderFailure(exc.code))
                requests += result.request_attempts
                self.attempted_requests += result.request_attempts
                self._daily_requests += result.request_attempts
                self._last_request = self.monotonic()
                if cancel.is_set():
                    cancelled = True
                    break  # No publication after disconnect.
                checked = self.clock()
                selected = [
                    d
                    for d in self._days(left, right)
                    if d in states and states[d].state != "NON_TRADING"
                ]
                if result.failure:
                    error = result.failure.code
                    self._provider_blocked_until = checked + timedelta(
                        seconds=self.policy.market_data_failure_backoff_seconds
                    )
                    for d in selected:
                        self._coverage[(key, d)] = Coverage(
                            "REJECTED"
                            if error in {"INVALID_DATA", "UNEXPECTED_RESPONSE"}
                            else "FAILED",
                            checked,
                            error,
                        )
                    break  # No retries/fallback and no further chunks after an execution failure.
                if result.status not in {
                    "VALIDATED_UNQUALIFIED",
                    "VALIDATED_WITH_GAPS_UNQUALIFIED",
                    "EMPTY_UNQUALIFIED",
                }:
                    error = "VALIDATION_REJECTED"
                    for d in selected:
                        self._coverage[(key, d)] = Coverage("REJECTED", checked, error)
                    break
                if result.observations:
                    collected = CollectedSeries(
                        listing,
                        left,
                        right,
                        digest({"provider": self.provider.identity, "start": left, "end": right}),
                        (result,),
                    )
                    try:
                        merged = self.store.merge(
                            instrument_id,
                            source_id,
                            collected,
                            max_rows=self.policy.market_data_max_rows,
                            refresh=refresh or bool(stale),
                        )
                        added += merged["added"]
                        revised += merged["revised"]
                    except APIError as exc:
                        error = exc.code
                        for d in selected:
                            self._coverage[(key, d)] = Coverage("REJECTED", checked, error)
                        break
                returned = {r.trading_date for r in result.observations}
                for d in selected:
                    self._coverage[(key, d)] = Coverage(
                        "AVAILABLE" if d in returned else "ATTEMPTED_EMPTY", checked
                    )
        final_rows = self.store.rows(instrument_id, source_id, "PROVIDER_ADJUSTED")
        final = self._states(key, listing, start, end, final_rows, self.clock(), eligible)
        counts = {}
        for d, entry in final.items():
            if d >= visible_start:
                counts[entry.state] = counts.get(entry.state, 0) + 1
        unresolved = any(
            v.state not in {"AVAILABLE", "NON_TRADING", "OUTSIDE_VERIFIED_HISTORY"}
            for v in final.values()
        )
        if error is None:
            error = next(
                (v.error for v in final.values() if v.state in {"FAILED", "REJECTED"} and v.error),
                None,
            )
        warmup_count = sum(r.trading_date < visible_start for r in final_rows)
        expected_prefix = (
            sorted((d for d in self._sessions if d < visible_start))[-warmup_bars:]
            if warmup_bars
            else []
        )
        warmup_complete = (
            not warmup_bars
            or len(expected_prefix) == warmup_bars
            and set(expected_prefix) <= {r.trading_date for r in final_rows}
        )
        return {
            "status": "CANCELLED"
            if cancelled
            else "PARTIAL"
            if unresolved or error
            else "UPDATED"
            if requests
            else "REUSED",
            "requests": requests,
            "added": added,
            "revised": revised,
            "error": error,
            "coverage": counts,
            "requested_start": visible_start.isoformat(),
            "requested_end": end.isoformat(),
            "acquisition_start": start.isoformat(),
            "warmup_requested": warmup_bars,
            "warmup_available": warmup_count,
            "warmup_complete": warmup_complete,
            "unavailable_dates": [
                {"date": d.isoformat(), "state": v.state}
                for d, v in final.items()
                if d >= visible_start and v.state != "AVAILABLE"
            ][:1000],
            "dataset_count": len(final_rows),
            "dataset_first_date": final_rows[0].trading_date.isoformat() if final_rows else None,
            "dataset_last_date": final_rows[-1].trading_date.isoformat() if final_rows else None,
            "latest_completed_session_candidate": completed.isoformat(),
            "latest_provider_eligible_session_candidate": eligible.isoformat(),
            "calendar_unassessed": any(self.session(d) is None for d in states),
            "source_qualified": False,
            "persistence": "NONE_PROCESS_MEMORY_ONLY",
        }
