"""Synthetic binary/connection/reconciliation tests. No provider network."""

from datetime import date, timedelta, timezone
from decimal import Decimal
import json
import struct
from threading import Event
from urllib.parse import parse_qs, urlsplit
import pytest
from fastapi.testclient import TestClient
from app.dhan_feed import decode, tick_price, exact_float32
from app.dhan_history_contract import INSTRUMENTS
from app.serialization import plain
from .test_market_session import setup
from .session_fixtures import NOW, TOKEN, CLIENT
from .conftest import TOKEN as APP_TOKEN, ORIGIN
from .provider_fixtures import collected, plan
from app.transient_uat import NAMES


def frame(code=4, sid=21401, epoch=None, *, value=101, volume=1000):
    # Python float conversion is test-fixture wire construction only.
    epoch = epoch or int(NOW.replace(tzinfo=timezone.utc).timestamp())
    body = (
        struct.pack("<fi", value, epoch)
        if code == 2
        else struct.pack("<fi", 100, 0)
        if code == 6
        else struct.pack("<fhifiii4f", value, 1, epoch, 100, volume, 1, 1, 100, 100, 102, 99)
    )
    return struct.pack("<BHBi", code, 8 + len(body), 1, sid) + body


@pytest.mark.parametrize("sid", [21401, 21428, 14428, 8080])
def test_verified_identity_decimal_tick_and_epoch(sid):
    e = decode(frame(sid=sid, value=101.23), NOW)
    assert e.prices["last_price"] == Decimal("101.23")
    assert isinstance(e.prices["last_price"], Decimal) and e.trade_at == NOW
    assert e.volume == 1000


@pytest.mark.parametrize("bits", [0x7F800000, 0x7FC00000, 0xBF800000, 0xFF800000])
def test_invalid_float32_rejected(bits):
    with pytest.raises(ValueError):
        exact_float32(bits)


def test_unique_tick_recovery_rejects_ambiguous_or_off_tick():
    packet = struct.pack("<f", 10000000.0)
    with pytest.raises(ValueError, match="AMBIGUOUS"):
        tick_price(packet, 0, Decimal(".01"))
    with pytest.raises(ValueError, match="AMBIGUOUS"):
        tick_price(struct.pack("<f", 101.235), 0, Decimal(".01"))
    assert tick_price(struct.pack("<f", 101.23), 0, Decimal(".01")) == Decimal("101.23")


@pytest.mark.parametrize(
    "defect",
    ["length", "segment", "unknown", "truncated", "future", "negative_volume", "bad_ohlc", "text"],
)
def test_strict_feed_validation(defect):
    packet = bytearray(frame())
    if defect == "length":
        packet[1:3] = struct.pack("<H", 49)
    if defect == "segment":
        packet[3] = 4
    if defect == "unknown":
        packet[4:8] = struct.pack("<i", 123456)
    if defect == "truncated":
        packet = packet[:-1]
    if defect == "future":
        packet[14:18] = struct.pack(
            "<i", int((NOW + timedelta(minutes=1)).replace(tzinfo=timezone.utc).timestamp())
        )
    if defect == "negative_volume":
        packet[22:26] = struct.pack("<i", -1)
    if defect == "bad_ohlc":
        packet[42:46] = struct.pack("<f", 98)
    if defect == "text":
        packet = "secret-bearing provider error"
    with pytest.raises(ValueError):
        decode(bytes(packet) if isinstance(packet, bytearray) else packet, NOW)


def test_prev_close_does_not_create_live_price_and_replay_is_not_double_counted():
    app, session, calls, _ = setup(market_stream_enabled=True)
    stream = app.state.market_stream
    stream.apply(decode(frame(6), NOW))
    assert not session.quotes and stream.updates == 0
    event = decode(frame(), NOW)
    stream.state = "CONNECTED"
    stream.apply(event)
    stream.apply(event)
    assert stream.updates == 1 and not calls
    quote = session.quotes[INSTRUMENTS[0].isin]
    assert quote.previous_close == Decimal(100) and quote.classification == "LIVE_STREAM"
    assert session.get_quotes()["quotes"][0]["last_price"] == Decimal(101) and not calls
    stream.apply(
        decode(
            frame(epoch=int((NOW - timedelta(seconds=1)).replace(tzinfo=timezone.utc).timestamp())),
            NOW,
        )
    )
    assert stream.rejected == 1


def test_new_session_ticker_cannot_carry_previous_day_ohlcv():
    app, s, _, _ = setup(market_stream_enabled=True)
    stream = app.state.market_stream
    stream.apply(decode(frame(), NOW))
    tomorrow = NOW + timedelta(days=1)
    stream.apply(
        decode(frame(2, epoch=int(tomorrow.replace(tzinfo=timezone.utc).timestamp())), tomorrow)
    )
    q = s.quotes[INSTRUMENTS[0].isin]
    assert q.volume is None and q.open is None and q.previous_close is None


class Socket:
    def __init__(self, stream, packets=()):
        self.stream = stream
        self.packets = list(packets)
        self.messages = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send(self, message):
        self.messages.append(json.loads(message))

    def recv(self, timeout):
        if self.packets:
            return self.packets.pop(0)
        self.stream._stop.set()
        raise TimeoutError()

    def ping(self):
        e = Event()
        e.set()
        return e


def await_thread(stream):
    stream._thread.join(timeout=5)
    assert not stream._thread.is_alive()


def test_one_shared_connection_secure_auth_subscription_and_shutdown(caplog):
    app, s, calls, _ = setup(market_stream_enabled=True)
    stream = app.state.market_stream
    socket = Socket(stream, [frame(6), frame()])
    urls = []

    def connect(url, **kwargs):
        urls.append(url)
        assert (
            kwargs["open_timeout"] == 8 and kwargs["max_size"] == 4096 and kwargs["proxy"] is None
        )
        assert kwargs["logger"].propagate is False
        return socket

    stream.connector = connect
    stream.start(manual=True)
    await_thread(stream)
    query = parse_qs(urlsplit(urls[0]).query)
    assert query["token"] == [TOKEN] and query["clientId"] == [CLIENT]
    assert socket.messages[0]["RequestCode"] == 17 and socket.messages[0]["InstrumentCount"] == 4
    assert {x["SecurityId"] for x in socket.messages[0]["InstrumentList"]} == {
        x.security_id for x in INSTRUMENTS
    }
    assert socket.messages[-1] == {"RequestCode": 12}
    assert stream.updates == 1 and stream.attempts == 1 and not calls
    assert TOKEN not in str(plain(stream.status())) + caplog.text
    assert CLIENT not in str(plain(stream.status())) + caplog.text


def test_bounded_reconnect_resubscription_and_exhaustion():
    app, s, _, _ = setup(market_stream_enabled=True)
    stream = app.state.market_stream
    attempts = []
    delays = []

    def broken(url, **kwargs):
        attempts.append(1)
        raise OSError("secret " + TOKEN)

    stream.connector = broken
    stream.retry_wait = lambda n: delays.append(n) or False
    stream.start(manual=True)
    await_thread(stream)
    assert len(attempts) == 4 and delays == [1, 2, 4] and stream.state == "EXHAUSTED"
    stream.start()
    assert len(attempts) == 4  # No auto reconnect storm.
    assert TOKEN not in str(stream.status())


def test_transient_disconnect_reconnects_and_restores_subscription():
    app, s, _, _ = setup(market_stream_enabled=True)
    stream = app.state.market_stream
    count = []
    sockets = []

    class Broken(Socket):
        def recv(self, timeout):
            raise OSError("temporary")

    def connect(url, **kwargs):
        socket = Broken(stream) if not count else Socket(stream, [frame()])
        count.append(1)
        sockets.append(socket)
        return socket

    stream.connector = connect
    stream.retry_wait = lambda _: False
    stream.start(manual=True)
    await_thread(stream)
    assert len(sockets) == 2 and all(x.messages[0]["RequestCode"] == 17 for x in sockets)
    assert stream.updates == 1


@pytest.mark.parametrize("code", [805, 806, 807, 808, 809, 810])
def test_provider_disconnect_is_terminal_and_sanitized(code):
    app, s, _, _ = setup(market_stream_enabled=True)
    stream = app.state.market_stream
    packet = struct.pack("<BHB i H", 50, 10, 0, 0, code)
    stream.connector = lambda *a, **k: Socket(stream, [packet])
    stream.start(manual=True)
    await_thread(stream)
    assert stream.attempts == 1 and stream.state == "BLOCKED" and str(code) in stream.error


def test_disabled_and_outside_hours_make_no_connection():
    app, s, _, clock = setup()
    stream = app.state.market_stream
    stream.connector = lambda *a, **k: pytest.fail("must not connect")
    assert stream.start(manual=True)["state"] == "DISABLED"
    s.settings.market_stream_enabled = True
    clock[0] = NOW.replace(hour=17)
    assert stream.start()["state"] == "PAUSED_OUTSIDE_SESSION"
    assert stream.attempts == 0


def test_viewer_cap_and_detach():
    app, *_ = setup()
    stream = app.state.market_stream
    for _ in range(16):
        stream.attach()
    with pytest.raises(Exception, match="viewer limit"):
        stream.attach()
    for _ in range(17):
        stream.detach()
    assert stream.subscribers == 0


def installed():
    app, s, calls, clock = setup()
    p = plan(date(2026, 11, 5), date(2026, 11, 6))
    _, collection, _ = collected(p)
    app.state.transient_research.install(collection, p, names=NAMES, data_class="SYNTHETIC_TEST")
    instrument = app.state.transient_research.listings()[0]
    return app, s, calls, clock, instrument


def test_reconciliation_daily_is_not_changed_and_revisions_are_auditable():
    app, s, calls, clock, i = installed()
    s.intraday(i.id, 5, "previous")
    before = app.state.transient_research.snapshot().rows(
        i.id, app.state.transient_research.sources()[0].id, "PROVIDER_ADJUSTED"
    )
    result = app.state.market_reconciliation.reconcile(i.id, date(2026, 11, 5))
    assert result["classification"] == "HISTORICAL_FINAL" and result["requests"] == 0
    assert result["provisional_disposition"] == "SUPERSEDED_BY_VALIDATED_PROVIDER_DAILY"
    assert result["provisional_bar_count"] == 75 and result["differing_fields"]
    assert result["comparison_status"] == "REVIEW_DIFFERENCES"
    after = app.state.transient_research.snapshot().rows(
        i.id, app.state.transient_research.sources()[0].id, "PROVIDER_ADJUSTED"
    )
    assert before == after
    assert app.state.market_reconciliation.status()["audit"]
    count = len(calls)
    app.state.market_reconciliation.reconcile(i.id, date(2026, 11, 5))
    assert len(calls) == count


def test_publication_delay_and_incomplete_intraday_are_explicit():
    app, s, calls, clock, i = installed()
    source = app.state.transient_research.sources()[0]
    # Isolated fixture removes today's daily row to model T-1 delay.
    data = app.state.transient_research._datasets[(i.id, source.id)]
    app.state.transient_research._datasets[(i.id, source.id)] = {
        **data,
        "rows": tuple(r for r in data["rows"] if r.trading_date < NOW.date()),
    }
    s.intraday(i.id, 5, "current")
    count = len(calls)
    r = app.state.market_reconciliation.reconcile(i.id, NOW.date())
    assert len(calls) == count and r["publication_state"] == "WAITING_T_MINUS_ONE"
    assert r["classification"] == "INTRADAY_PROVISIONAL" and r["provisional_coverage"] == "PARTIAL"


def test_sse_authentication_origin_and_control_do_not_expose_credentials():
    app, s, calls, _ = setup()
    with TestClient(app, base_url="http://localhost") as client:
        assert client.get("/api/v1/market-data/stream-events").status_code == 401
        headers = {"Authorization": "Bearer " + APP_TOKEN}
        assert client.get("/api/v1/market-data/stream-events", headers=headers).status_code == 403
        response = client.post(
            "/api/v1/market-data/stream-control",
            headers={**headers, "Origin": ORIGIN},
            json={"action": "connect"},
        )
        assert response.status_code == 200 and response.json()["data"]["state"] == "DISABLED"
        assert TOKEN not in response.text and CLIENT not in response.text and not calls


def test_fixed_host_connector_does_not_retry_http_auth_rejection(monkeypatch):
    from app import feed_connection as connection
    from websockets.exceptions import InvalidStatus
    from websockets.http11 import Response
    from websockets.datastructures import Headers
    import socket

    calls = []

    class Transport:
        def settimeout(self, value):
            assert 0 < value <= 2

        def connect(self, address):
            calls.append(address)

        def close(self):
            pass

    monkeypatch.setattr(
        connection,
        "addresses",
        lambda: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))] * 2,
    )
    monkeypatch.setattr(connection.socket, "socket", lambda *a: Transport())

    def rejected(*a, **k):
        raise InvalidStatus(Response(401, "Unauthorized", Headers()))

    monkeypatch.setattr(connection, "connect", rejected)
    with pytest.raises(InvalidStatus):
        connection.connect_feed("wss://api-feed.dhan.co?synthetic=only")
    assert len(calls) == 1


def test_next_session_publication_validates_and_promotes_without_tick_contamination():
    import httpx
    from .provider_fixtures import body_for
    from .session_fixtures import intraday_body

    future = [NOW.replace(hour=16)]
    calendar = plan(date(2026, 10, 1), date(2026, 11, 6)).calendar

    def handler(request, n):
        return (
            httpx.Response(
                200,
                content=body_for(request, calendar),
                headers={"Content-Type": "application/json"},
            )
            if request.url.path.endswith("/historical")
            else httpx.Response(200, json=intraday_body(request, future[0]))
        )

    app, s, calls, clock = setup(handler=handler)
    clock[0] = future[0]
    s.provider.clock = lambda: clock[0]
    instrument = app.state.transient_research.listings()[0]
    s.intraday(instrument.id, 5, "current")
    r = app.state.market_reconciliation.reconcile(instrument.id, NOW.date())
    assert (
        r["publication_state"] == "WAITING_T_MINUS_ONE"
        and r["provisional_coverage"] == "COMPLETE_REGULAR_SESSION"
    )
    assert r["classification"] == "INTRADAY_PROVISIONAL"
    clock[0] += timedelta(days=1)
    final = app.state.market_reconciliation.reconcile(instrument.id, NOW.date())
    assert final["error"] is None, final["error"]
    assert final["requests"] == 1, final["publication_state"]
    assert final["classification"] == "HISTORICAL_FINAL"
    assert final["official_observation_id"] and final["official_batch_id"]
    assert app.state.market_reconciliation.superseded(instrument.id, NOW.date())
    assert final["provisional_hash"] == r["provisional_hash"]
    count = len(calls)
    again = app.state.market_reconciliation.reconcile(instrument.id, NOW.date())
    assert again["requests"] == 0 and len(calls) == count
    assert sum(request.url.path.endswith("/historical") for request in calls) == 1
    source = app.state.transient_research.sources()[0]
    rows = app.state.transient_research.rows(instrument.id, source.id, "PROVIDER_ADJUSTED")
    assert len(rows) == 1 and rows[0].close == Decimal(101)


def test_manual_rest_response_cannot_roll_back_a_newer_stream_price():
    app, s, calls, clock = setup(market_stream_enabled=True)
    stream = app.state.market_stream
    newer = NOW + timedelta(seconds=2)
    stream.apply(
        decode(
            frame(epoch=int(newer.replace(tzinfo=timezone.utc).timestamp()), value=101.23), newer
        )
    )
    before = s.quotes[INSTRUMENTS[0].isin]
    s.get_quotes(refresh=True)
    assert len(calls) == 1 and s.quotes[INSTRUMENTS[0].isin] is before


def test_stream_uses_injected_verified_catalog_not_a_second_identity_map():
    from dataclasses import replace
    from app.market_stream import MarketStream

    app, s, _, _ = setup(market_stream_enabled=True)
    s.provider._instruments = (
        replace(INSTRUMENTS[0], symbol="SYNTH_VERIFIED", security_id="12345", isin="INF000000001"),
    )
    stream = MarketStream(s)
    socket = Socket(stream)
    stream.connector = lambda *a, **k: socket
    stream.start(manual=True)
    await_thread(stream)
    assert socket.messages[0]["InstrumentCount"] == 1
    assert socket.messages[0]["InstrumentList"][0]["SecurityId"] == "12345"
