"""One shared backend-only read-only feed. Bounded reconnect/idle/frames/subscribers.

Provider authentication URL is constructed only inside the connector; exceptions,
frames and URLs are never logged. No provider SDK or trading surface is imported.
"""

import json
import logging
from threading import Event, RLock, Thread
import time
from urllib.parse import urlencode
from .feed_connection import connect_feed
from websockets.exceptions import InvalidStatus
from .dhan_feed import decode
from .dhan_history_diagnostic import configuration_problem
from .market_session import MarketQuote, session_state
from .errors import APIError


QUIET = logging.Logger("bullion.private.marketfeed", level=logging.CRITICAL + 1)
QUIET.addHandler(logging.NullHandler())
QUIET.propagate = False


class MarketStream:
    def __init__(self, session, *, connector=connect_feed, monotonic=time.monotonic):
        self.session, self.connector, self.monotonic = session, connector, monotonic
        self.catalog = tuple(session.provider._instruments)
        self._lock, self._stop = RLock(), Event()
        self._thread = None
        self.state, self.error = "DISCONNECTED", None
        self.generation = self.attempts = self.frames = self.rejected = self.updates = 0
        self.subscribers = 0
        self.last_view = self.monotonic()
        self.last_received = None
        self.by_symbol = {}
        self.rejection_reasons = {}
        self.previous_close = {}
        self.retry_wait = self._stop.wait
        self._manual = False

    def status(self):
        with self._lock:
            return {
                "state": self.state,
                "error": self.error,
                "generation": self.generation,
                "connection_attempts": self.attempts,
                "frames": self.frames,
                "rejected_frames": self.rejected,
                "rejection_reasons": dict(self.rejection_reasons),
                "price_updates": self.updates,
                "subscribers": self.subscribers,
                "last_received_at": self.last_received,
                "instruments": [x.symbol for x in self.catalog],
                "per_instrument": [dict(symbol=k, **v) for k, v in self.by_symbol.items()],
                "max_connections": 1,
                "max_reconnects": 3,
                "retention": "PROCESS_MEMORY_ONLY",
                "enabled": self.session.settings.market_stream_enabled,
            }

    def healthy(self):
        with self._lock:
            return (
                self.state == "CONNECTED"
                and self.last_received is not None
                and (self.session.clock() - self.last_received).total_seconds() < 30
            )

    def attach(self):
        with self._lock:
            if self.subscribers >= 16:
                raise APIError(429, "STREAM_SUBSCRIBER_LIMIT", "Local stream viewer limit reached.")
            self.subscribers += 1
            self.last_view = self.monotonic()

    def detach(self):
        with self._lock:
            self.subscribers = max(0, self.subscribers - 1)
            self.last_view = self.monotonic()

    def start(self, *, manual=False):
        with self._lock:
            if not (
                self.session.settings.market_data_enabled
                and self.session.settings.market_stream_enabled
            ):
                self.state, self.error = "DISABLED", "MARKET_STREAM_DISABLED"
                return self.status()
            if self._thread and self._thread.is_alive():
                return self.status()
            if not manual and (
                self.state in {"EXHAUSTED", "BLOCKED", "DISCONNECTED"} and self.generation
            ):
                return self.status()  # Explicit retry only after exhaustion/user disconnect.
            if (
                not manual
                and session_state(self.session.clock(), self.session.daily.calendar) != "OPEN"
            ):
                self.state = "PAUSED_OUTSIDE_SESSION"
                return self.status()
            config = self.session.provider._config
            problem = configuration_problem(config)
            if problem or not config.credentials or not config.credentials.client_id:
                self.state, self.error = "BLOCKED", problem or "MISSING_CLIENT_ID"
                return self.status()
            if len(self.catalog) > 100 or any(not x.tick_size_paise for x in self.catalog):
                self.state, self.error = "BLOCKED", "UNVERIFIED_SUBSCRIPTION_METADATA"
                return self.status()
            self._stop.clear()
            self._manual, self.error = manual, None
            self.generation += 1
            self.state = "CONNECTING"
            self.last_view = self.monotonic()
            self._thread = Thread(target=self._run, name="read-only-market-feed", daemon=True)
            self._thread.start()
            return self.status()

    def stop(self):
        self._stop.set()
        thread = self._thread
        if thread:
            thread.join(timeout=12)
        with self._lock:
            if not thread or not thread.is_alive():
                self.state = "DISCONNECTED"
        return self.status()

    def apply(self, event):
        with self._lock:
            self.frames += 1
            self.last_received = event.received_at or self.session.clock()
            if event.code == 50:
                return
            if event.code == 6:
                self.previous_close[event.isin] = (
                    event.prices["previous_close"],
                    event.received_at.astimezone(self.session.ist).date(),
                )
                return  # Previous-close evidence is never a current-price event.
            if event.code not in {2, 4}:
                return
            with self.session._quote_lock:
                old = self.session.quotes.get(event.isin)
                if old and old.last_trade_at and event.trade_at < old.last_trade_at:
                    self.rejected += 1
                    return
                # Same-second identical replay doesn't refresh freshness or double-count.
                if (
                    old
                    and old.last_trade_at == event.trade_at
                    and old.last_price == event.prices["last_price"]
                    and (event.volume is None or old.volume == event.volume)
                    and old.classification == "LIVE_STREAM"
                ):
                    return
                listing = next(x for x in self.session.provider.listings() if x.isin == event.isin)
                previous = self.previous_close.get(event.isin)
                baseline = (
                    previous[0]
                    if previous
                    and previous[1] == event.trade_at.astimezone(self.session.ist).date()
                    else None
                )
                same_day = (
                    old
                    and old.last_trade_at
                    and old.last_trade_at.astimezone(self.session.ist).date()
                    == event.trade_at.astimezone(self.session.ist).date()
                )
                # Never carry a previous session's OHLC/volume into a ticker-only new day.
                values = {
                    k: event.prices.get(k, getattr(old, k, None) if same_day else None)
                    for k in ("open", "high", "low", "provider_close")
                }
                self.session.quotes[event.isin] = MarketQuote(
                    listing=listing,
                    last_price=event.prices["last_price"],
                    **values,
                    previous_close=baseline or (old.previous_close if same_day else None),
                    volume=event.volume
                    if event.volume is not None
                    else old.volume
                    if same_day
                    else None,
                    last_trade_at=event.trade_at,
                    retrieved_at=event.received_at,
                    previous_close_basis="EXPLICIT_PREVIOUS_CLOSE_FEED_PACKET"
                    if baseline
                    else old.previous_close_basis
                    if same_day
                    else "UNAVAILABLE",
                    classification="LIVE_STREAM",
                    warnings=(
                        "FLOAT32_UNIQUE_VERIFIED_TICK_RECOVERY",
                        "FEED_UTC_CLOCK_FIELDS_AS_IST_PROVISIONALLY_CORROBORATED",
                        "PRICE_ADJUSTMENT_UNQUALIFIED",
                        "TRANSIENT_MEMORY_ONLY",
                    ),
                )
                self.session.quote_generation += 1
                self.updates += 1
                previous = self.by_symbol.get(event.symbol, {})
                self.by_symbol[event.symbol] = {
                    "updates": previous.get("updates", 0) + 1,
                    "latest_provider_timestamp": event.trade_at,
                    "wire_epoch_seconds": event.wire_epoch_seconds,
                    "timestamp_policy": "SDK_UTC_CLOCK_FIELDS_AS_IST_CANDIDATE_V1",
                    "retrieved_at": event.received_at,
                }

    def _run(self):
        config = self.session.provider._config.credentials
        # Sole consumer of secret URL. Fixed host, TLS verified; private quiet logger.
        url = "wss://api-feed.dhan.co?" + urlencode(
            {
                "version": "2",
                "token": config.access_token.get_secret_value(),
                "clientId": config.client_id.get_secret_value(),
                "authType": "2",
            }
        )
        for attempt in range(4):
            if self._stop.is_set():
                break
            try:
                with self._lock:
                    self.attempts += 1
                    self.state = "CONNECTING" if attempt == 0 else "RECONNECTING"
                with self.connector(
                    url,
                    open_timeout=8,
                    close_timeout=2,
                    max_size=4096,
                    max_queue=16,
                    logger=QUIET,
                    proxy=None,
                    ping_interval=None,
                ) as socket:
                    socket.send(
                        json.dumps(
                            {
                                "RequestCode": 17,
                                "InstrumentCount": len(self.catalog),
                                "InstrumentList": [
                                    {"ExchangeSegment": "NSE_EQ", "SecurityId": x.security_id}
                                    for x in self.catalog
                                ],
                            }
                        )
                    )
                    with self._lock:
                        self.state, self.error = "CONNECTED", None
                        self.previous_close = {}  # Fresh subscription evidence for each connection.
                    ping_at = self.monotonic()
                    while not self._stop.is_set():
                        if self.monotonic() - self.last_view > 30 and not self.subscribers:
                            break
                        if (
                            not self._manual
                            and session_state(self.session.clock(), self.session.daily.calendar)
                            != "OPEN"
                        ):
                            break
                        try:
                            packet = socket.recv(timeout=1)
                        except TimeoutError:
                            packet = None
                        if packet is not None:
                            try:
                                event = decode(packet, self.session.clock())
                                if event.code == 50:
                                    with self._lock:
                                        self.state, self.error = (
                                            "BLOCKED",
                                            "FEED_DISCONNECT_" + str(event.disconnect_code),
                                        )
                                    return  # Provider disconnects are never automatically retried.
                                self.apply(event)
                            except ValueError as exc:
                                allowed = {
                                    "INVALID_FEED_FRAME",
                                    "INVALID_FEED_LENGTH",
                                    "UNSUBSCRIBED_FEED_IDENTITY",
                                    "UNSUPPORTED_FEED_STRUCTURE",
                                    "INVALID_WIRE_PRICE",
                                    "AMBIGUOUS_WIRE_PRICE",
                                    "INVALID_FEED_TIMESTAMP",
                                    "FUTURE_FEED_TIMESTAMP",
                                    "INVALID_FEED_VOLUME",
                                    "INCONSISTENT_FEED_OHLC",
                                }
                                reason = (
                                    exc.args[0]
                                    if exc.args and exc.args[0] in allowed
                                    else "INVALID_FEED_FRAME"
                                )
                                with self._lock:
                                    self.rejected += 1
                                    self.rejection_reasons[reason] = (
                                        self.rejection_reasons.get(reason, 0) + 1
                                    )
                        if self.monotonic() - ping_at >= 10:
                            if not socket.ping().wait(timeout=5):
                                raise TimeoutError()
                            ping_at = self.monotonic()
                    try:
                        socket.send('{"RequestCode":12}')
                    except Exception:
                        pass
                    break
            except InvalidStatus as exc:
                status = exc.response.status_code
                with self._lock:
                    self.error = "FEED_HTTP_" + str(status)
                    self.state = "BLOCKED" if status in {400, 401, 403, 429} else "RECONNECTING"
                if status in {400, 401, 403, 429}:
                    return
            except Exception:
                with self._lock:
                    self.error = "FEED_CONNECTION_UNAVAILABLE"
            if attempt == 3:
                with self._lock:
                    self.state = "EXHAUSTED"
                return
            if self.retry_wait(2**attempt):
                break
        with self._lock:
            self.state = "DISCONNECTED" if self._stop.is_set() else "PAUSED_IDLE_OR_SESSION"
