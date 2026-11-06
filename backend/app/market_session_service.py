"""P0 quote/intraday orchestration over bounded RAM snapshots; no persistent I/O."""

from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from decimal import Context, ROUND_HALF_EVEN, localcontext
from threading import Event, RLock
from .analytics import Point, indicator_values, wire, MAX_POINTS
from .errors import APIError
from .market_session import IST, INTERVALS, session_state, regular_bounds
from .serialization import digest, plain
from .provider_budget import operation_slot


class MarketSessionService:
    def __init__(self, provider, daily, settings, budget, *, clock=None):
        self.ist = IST
        self.stream = None
        self.provider, self.daily, self.settings, self.budget = provider, daily, settings, budget
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self._quote_lock = RLock()
        self._intraday_lock = RLock()
        self.quotes = {}
        self.quote_generation = 0
        self.quote_checked = None
        self.quote_error = None
        self.candles = {}
        self.coverage = {}
        self.revisions = {}
        self.receipts = []
        self.quote_attempts = self.intraday_attempts = 0

    def policy(self):
        now = self.clock()
        state = session_state(now, self.daily.calendar)
        return {
            "enabled": self.settings.market_data_enabled,
            "quotes_enabled": self.settings.market_quotes_enabled,
            "intraday_enabled": self.settings.market_intraday_enabled,
            "quote_refresh_seconds": self.settings.market_quote_refresh_seconds,
            "auto_quote_refresh_seconds": self.settings.market_quote_refresh_seconds
            if state == "OPEN"
            else 0,
            "intraday_refresh_seconds": self.settings.market_intraday_refresh_seconds,
            "session_state": state,
            "today": now.astimezone(IST).date(),
            "intervals": INTERVALS,
            "quote_requests": self.quote_attempts,
            "intraday_requests": self.intraday_attempts,
            "provider_requests_today": self.budget.attempts,
            "retention": "BOUNDED_PROCESS_MEMORY_ONLY",
            "timestamp_policy": getattr(self.provider, "timestamp_policy", "UNASSESSED"),
        }

    def resolve(self, instrument_id):
        instrument = next((i for i in self.daily.store.listings() if i.id == instrument_id), None)
        if instrument is None:
            raise APIError(422, "UNVERIFIED_INSTRUMENT", "Select a configured provider instrument.")
        listing = next(
            (
                x
                for x in self.provider.listings()
                if (x.isin, x.symbol, x.exchange, x.currency)
                == (instrument.isin, instrument.symbol, instrument.exchange, instrument.currency)
            ),
            None,
        )
        if listing is None:
            raise APIError(422, "UNVERIFIED_INSTRUMENT", "Full verified identity required.")
        return instrument, listing

    def _receipt(self, kind, result):
        symbols = [q.listing.symbol for q in result.quotes] or sorted(
            {r.listing.symbol for r in result.candles}
        )
        interval = result.candles[0].interval if result.candles else None
        self.receipts = (
            self.receipts
            + [{"kind": kind, "symbols": symbols, "interval": interval, **plain(result.summary())}]
        )[-256:]

    def quote_view(self, quote, now, state):
        result = asdict(quote)
        result["volume"] = str(quote.volume) if quote.volume is not None else None
        event_age = (
            max(0, int((now - quote.last_trade_at).total_seconds()))
            if quote.last_trade_at
            else None
        )
        retrieval_age = max(0, int((now - quote.retrieved_at).total_seconds()))
        freshness = (
            "UNASSESSED"
            if event_age is None
            else "STALE"
            if max(event_age, retrieval_age) > self.settings.market_quote_stale_seconds
            else "FRESH"
        )
        result.update(
            freshness=freshness,
            market_session=state,
            last_trade_age_seconds=event_age,
            retrieval_age_seconds=retrieval_age,
            absolute_change=None,
            percent_change=None,
        )
        if quote.previous_close is not None:
            with localcontext(Context(prec=34, rounding=ROUND_HALF_EVEN)):
                result["absolute_change"] = wire(quote.last_price - quote.previous_close)
                result["percent_change"] = wire(
                    (quote.last_price - quote.previous_close) / quote.previous_close * 100
                )
        return result

    def get_quotes(self, *, refresh=False, cached_only=False):
        generation = self.quote_generation
        stream_healthy = self.stream is not None and self.stream.healthy()
        with operation_slot(self._quote_lock):
            now = self.clock()
            error = None
            allowed = self.settings.market_data_enabled and self.settings.market_quotes_enabled
            due = (
                self.quote_checked is None
                or (now - self.quote_checked).total_seconds()
                >= self.settings.market_quote_refresh_seconds
            )
            if self.quotes and session_state(now, self.daily.calendar) != "OPEN":
                due = False
            if refresh and self.quote_generation == generation:
                due = True
            if not allowed:
                error = "MARKET_QUOTES_DISABLED"
            elif due and not cached_only and not (stream_healthy and not refresh):
                try:
                    result = self.budget.invoke(self.provider.retrieve_quotes)
                    self.quote_attempts += result.request_attempts
                    self._receipt("QUOTE", result)
                    self.quote_checked = self.clock()
                    self.quote_generation += 1
                    error = (
                        result.failure.code
                        if result.failure
                        else "PARTIAL_QUOTES"
                        if result.issues
                        else None
                    )
                    for quote in result.quotes:
                        previous = self.quotes.get(quote.listing.isin)
                        if previous and previous.last_trade_at and (
                            quote.last_trade_at is None or quote.last_trade_at < previous.last_trade_at
                        ):
                            continue  # A REST fallback/manual response cannot roll back a newer feed event.
                        self.quotes[quote.listing.isin] = quote
                    self.quote_error = error
                except APIError as exc:
                    error = exc.code
            else:
                error = self.quote_error
            now = self.clock()
            state = session_state(now, self.daily.calendar)
            records = []
            for instrument in self.daily.store.listings():
                quote = self.quotes.get(instrument.isin)
                if quote:
                    records.append(
                        {
                            "instrument_id": str(instrument.id),
                            "name": instrument.name,
                            **self.quote_view(quote, now, state),
                        }
                    )
                else:
                    records.append(
                        {
                            "instrument_id": str(instrument.id),
                            "name": instrument.name,
                            "listing": {
                                "symbol": instrument.symbol,
                                "isin": instrument.isin,
                                "currency": instrument.currency,
                            },
                            "classification": "UNAVAILABLE",
                            "freshness": "UNAVAILABLE",
                            "last_price": None,
                        }
                    )
            return {
                "quotes": records,
                "error": error,
                "policy": self.policy(),
                "checked_at": self.quote_checked,
                "status": "PARTIAL" if error else "AVAILABLE",
                "source": self.provider.identity,
                "transient": True,
            }

    def date_range(self, preset, start, end):
        today = self.clock().astimezone(IST).date()
        sessions = sorted(d for d in self.daily._sessions if d < today)
        if preset == "current":
            return today, today
        if preset == "previous":
            if not sessions:
                raise APIError(
                    422, "CALENDAR_UNASSESSED", "No reviewed previous session is available."
                )
            return sessions[-1], sessions[-1]
        if preset == "five":
            include = [today] if self.daily.session(today) is True else []
            days = (sessions + include)[-5:]
            if len(days) < 5:
                raise APIError(
                    422, "CALENDAR_UNASSESSED", "Five reviewed sessions are unavailable."
                )
            return days[0], days[-1]
        if preset == "thirty":
            return today - timedelta(days=29), today
        if (
            preset != "custom"
            or start is None
            or end is None
            or not date(2000, 1, 1) <= start <= end < date(2100, 1, 1)
            or (end - start).days > 366
        ):
            raise APIError(
                422,
                "INVALID_INTRADAY_RANGE",
                "Use an ordered custom range of at most 367 calendar days.",
            )
        return start, min(end, today)

    def _prefix(self, start, interval, warmup):
        if not warmup:
            return start
        sessions_needed = (warmup * interval + 374) // 375 + 1
        prior = sorted(d for d in self.daily._sessions if d < start)
        if len(prior) >= sessions_needed:
            return prior[-sessions_needed]
        return max(date(2000, 1, 1), start - timedelta(days=min(366, sessions_needed * 2 + 7)))

    def intraday(
        self,
        instrument_id,
        interval,
        preset="current",
        start=None,
        end=None,
        *,
        indicators=None,
        refresh=False,
        cancel=None,
    ):
        cancel = cancel or Event()
        indicators = indicators or {}
        if interval not in INTERVALS or type(interval) is not int:
            raise APIError(422, "INVALID_INTERVAL", "Choose a documented intraday interval.")
        for method, n in indicators.items():
            if (
                method not in {"SMA", "EMA", "RSI"}
                or type(n) is not int
                or not (2 if method == "RSI" else 1) <= n <= 10000
            ):
                raise APIError(
                    422,
                    "INVALID_INDICATOR_PARAMETERS",
                    "Use explicit supported observed-bar lookbacks.",
                )
        instrument, listing = self.resolve(instrument_id)
        start, end = self.date_range(preset, start, end)
        if start > end:
            raise APIError(422, "FUTURE_RANGE", "No completed/current session is in this range.")
        warmup = max((n + (1 if m == "RSI" else 0) for m, n in indicators.items()), default=0)
        acquisition_start = self._prefix(start, interval, warmup)
        key = (listing.isin, interval)
        requests = 0
        error = None
        with operation_slot(self._intraday_lock, cancel):
            now = self.clock()
            today = now.astimezone(IST).date()
            days = [
                acquisition_start + timedelta(days=i)
                for i in range((end - acquisition_start).days + 1)
            ]
            if (
                len(self.coverage) + sum((key, d) not in self.coverage for d in days)
                > self.settings.market_data_max_coverage_days
            ):
                raise APIError(
                    409, "COVERAGE_MEMORY_LIMIT", "Intraday coverage metadata capacity reached."
                )
            need = []
            for day in days:
                if self.daily.session(day) is False:
                    continue
                checked = self.coverage.get((key, day))
                ttl = self.settings.market_intraday_refresh_seconds if day == today else 86400
                if checked and checked[1] != "COMPLETE":
                    ttl = max(300, self.settings.market_intraday_refresh_seconds)
                if refresh or not checked or (now - checked[0]).total_seconds() >= ttl:
                    need.append(day)
            ranges = []
            for day in need:
                if (
                    ranges
                    and (day - ranges[-1][0]).days < self.settings.market_intraday_partition_days
                    and all(
                        self.daily.session(ranges[-1][1] + timedelta(days=i)) is False
                        for i in range(1, (day - ranges[-1][1]).days)
                    )
                ):
                    ranges[-1] = (ranges[-1][0], day)
                else:
                    ranges.append((day, day))
            if need and not (
                self.settings.market_data_enabled and self.settings.market_intraday_enabled
            ):
                error = "MARKET_INTRADAY_DISABLED"
            elif need:
                for left, right in ranges[: self.settings.market_session_max_requests]:
                    if cancel.is_set():
                        error = "CANCELLED"
                        break
                    try:
                        result = self.budget.invoke(
                            lambda: self.provider.retrieve_intraday(listing, interval, left, right)
                        )
                    except APIError as exc:
                        error = exc.code
                        break
                    requests += result.request_attempts
                    self.intraday_attempts += result.request_attempts
                    self._receipt("INTRADAY", result)
                    if result.failure:
                        error = result.failure.code
                        for day in need:
                            if left <= day <= right:
                                self.coverage[(key, day)] = (self.clock(), "FAILED")
                        break
                    existing = self.candles.get(key, {})
                    merged = {**existing, **{r.start: r for r in result.candles}}
                    total = sum(len(v) for k, v in self.candles.items() if k != key) + len(merged)
                    if total > self.settings.market_session_max_rows:
                        error = "INTRADAY_MEMORY_LIMIT"
                        break
                    self.candles = {**self.candles, key: merged}
                    if result.candles:
                        self.revisions[key] = self.revisions.get(key, 0) + 1
                    for day in need:
                        if left <= day <= right:
                            present = [r for r in merged.values() if r.start.date() == day]
                            expected = self.expected_starts(day, interval, self.clock())
                            complete = expected is not None and set(expected) <= {
                                r.start for r in present
                            }
                            self.coverage[(key, day)] = (
                                self.clock(),
                                "COMPLETE" if complete else "EMPTY" if not present else "PARTIAL",
                            )
            snapshot = tuple(sorted(self.candles.get(key, {}).values(), key=lambda r: r.start))
            revision = self.revisions.get(key, 0)
        return self.intraday_view(
            listing,
            instrument,
            interval,
            start,
            end,
            acquisition_start,
            snapshot,
            revision,
            indicators,
            requests,
            error,
        )

    def expected_starts(self, day, interval, now):
        if self.daily.session(day) is not True:
            return None
        opening, closing = regular_bounds(day)
        limit = min(closing, now.astimezone(IST) - timedelta(seconds=60))
        values = []
        stamp = opening
        while stamp < closing:
            if min(stamp + timedelta(minutes=interval), closing) <= limit:
                values.append(stamp)
            stamp += timedelta(minutes=interval)
        return values

    def intraday_view(
        self,
        listing,
        instrument,
        interval,
        start,
        end,
        acquisition_start,
        snapshot,
        revision,
        indicators,
        requests,
        error,
    ):
        now = self.clock()
        prefix = [r for r in snapshot if acquisition_start <= r.start.date() <= end]
        if len(prefix) > MAX_POINTS:
            raise APIError(
                422,
                "ANALYTICS_RANGE_LIMIT",
                "More than 10000 intraday bars; narrow dates or increase interval.",
            )
        completed = [r for r in prefix if r.classification == "INTRADAY_COMPLETED"]
        visible = [r for r in prefix if start <= r.start.date() <= end]
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        missing = []
        unknown = False
        for day in days:
            expected = self.expected_starts(day, interval, now)
            if expected is None:
                unknown = True
            else:
                missing.extend(d for d in expected if d not in {r.start for r in visible})
        points = [
            Point(
                r.start,
                r.close,
                canonical_hash=digest({"start": r.start, "close": r.close, "interval": interval}),
            )
            for r in completed
        ]
        breaks = {}
        for previous, current in zip(completed, completed[1:]):
            if previous.start.date() == current.start.date() and current.start != previous.end:
                breaks[current.start] = "MISSING_INTRADAY_CANDLE"
            elif previous.start.date() != current.start.date():
                in_between = [
                    d
                    for d in self.daily._sessions
                    if previous.start.date() < d < current.start.date()
                ]
                if (
                    in_between
                    or current.start != regular_bounds(current.start.date())[0]
                    or previous.end != regular_bounds(previous.start.date())[1]
                ):
                    breaks[current.start] = "INCOMPLETE_SESSION_BOUNDARY"
        calculated = {}
        for method, n in indicators.items():
            values = indicator_values(points, method, n, breaks)
            calculated[method] = {
                "n": n,
                "timeframe": str(interval) + "m",
                "algorithm_version": "decimal-research-v1",
                "values": [
                    {
                        "candle_start": v["trading_date"],
                        **{k: x for k, x in v.items() if k != "trading_date"},
                    }
                    for v in values
                    if start <= v["trading_date"].date() <= end
                ],
            }
        today = now.astimezone(IST).date()
        current = [r for r in snapshot if r.start.date() == today]
        provisional = None
        if current:
            expected = self.expected_starts(today, interval, now)
            provisional = {
                "classification": "PROVISIONAL - INTRADAY AGGREGATED",
                "session_date": today,
                "open": current[0].open,
                "high": max(r.high for r in current),
                "low": min(r.low for r in current),
                "close": current[-1].close,
                "volume": str(sum(r.volume for r in current))
                if all(r.volume_semantics == "PER_CANDLE_VOLUME" for r in current)
                else None,
                "volume_policy": "SUM_NON_OVERLAPPING_PROVIDER_CANDLE_VOLUMES_CORROBORATED_1M_5M",
                "coverage": "UNASSESSED"
                if expected is None
                else "INCOMPLETE"
                if set(expected) - {r.start for r in current}
                else "COMPLETE_TO_AVAILABLE_COMPLETED_BARS",
                "not_official_daily_close": True,
            }
        if provisional and getattr(self, "reconciliation", None) and self.reconciliation.superseded(instrument.id, today):
            provisional = {**provisional, "classification": "SUPERSEDED_BY_HISTORICAL_FINAL", "superseded": True}
        latest = max((r.retrieved_at for r in visible), default=None)
        return {
            "instrument_id": str(instrument.id),
            "listing": asdict(listing),
            "interval_minutes": interval,
            "exchange_timezone": "Asia/Kolkata",
            "price_basis": "INTRADAY_PROVIDER_ADJUSTMENT_UNQUALIFIED",
            "requested_period": {"start": start, "end": end},
            "acquisition_start": acquisition_start,
            "candles": [
                {
                    **{k: v for k, v in asdict(r).items() if k != "source_timestamp"},
                    "volume": str(r.volume),
                }
                for r in visible
            ],
            "indicators": calculated,
            "provisional_session": provisional,
            "status": "PARTIAL"
            if error or missing or unknown
            else "AVAILABLE"
            if visible
            else "UNAVAILABLE",
            "error": error,
            "requests": requests,
            "revision": revision,
            "missing_completed_candles": len(missing),
            "missing_timestamps": missing[:1000],
            "calendar_unassessed": unknown,
            "last_successful_retrieval": latest,
            "latest_provider_timestamp": visible[-1].start if visible else None,
            "freshness": "UNAVAILABLE"
            if latest is None
            else "STALE"
            if (now - latest).total_seconds() > self.settings.market_intraday_refresh_seconds * 2
            else "FRESH",
            "market_session": session_state(now, self.daily.calendar),
            "warmup_bars": warmup_count(completed, start),
            "warnings": [
                "PROVISIONAL_TIMESTAMP_AND_ADJUSTMENT_QUALIFICATION",
                "NO_POINT_IN_TIME_REPLAY_QUALIFICATION",
                "TRANSIENT_MEMORY_ONLY",
            ],
            "persistence": "NONE",
            "source": self.provider.identity,
        }


def warmup_count(rows, start):
    return sum(r.start.date() < start for r in rows)
