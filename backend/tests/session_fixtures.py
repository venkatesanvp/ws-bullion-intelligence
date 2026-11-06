"""Synthetic market-session HTTP fixtures; never actual market observations."""

from datetime import date, datetime, timedelta
import json
import httpx
from app.dhan_config import load_dhan_configuration
from app.dhan_market_provider import DhanMarketProvider
from app.dhan_history_contract import INSTRUMENTS
from app.market_session import IST, regular_bounds

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=IST)
TOKEN = "synthetic-session-access-token-never-a-real-credential"
CLIENT = "synthetic-session-client-id"


def quote_body(now=NOW):
    return {
        "status": "success",
        "data": {
            "NSE_EQ": {
                x.security_id: {
                    "last_price": 101,
                    "net_change": 1,
                    "ohlc": {"open": 100, "high": 102, "low": 99, "close": 100},
                    "volume": 1000,
                    "last_trade_time": now.strftime("%d/%m/%Y %H:%M:%S"),
                }
                for x in INSTRUMENTS
            }
        },
    }


def intraday_body(request, now=NOW):
    body = json.loads(request.content)
    interval = int(body["interval"])
    start = date.fromisoformat(body["fromDate"][:10])
    end = date.fromisoformat(body["toDate"][:10])
    stamps = []
    day = start
    while day < end:
        if day.weekday() < 5:
            stamp, close = regular_bounds(day)
            while stamp < close and stamp <= now:
                stamps.append(int(stamp.timestamp()))
                stamp += timedelta(minutes=interval)
        day += timedelta(days=1)
    return {
        "open": [100] * len(stamps),
        "high": [102] * len(stamps),
        "low": [99] * len(stamps),
        "close": [101] * len(stamps),
        "volume": [1000] * len(stamps),
        "timestamp": stamps,
    }


def provider_for_session(*, handler=None, now=NOW):
    calls = []

    def respond(request):
        calls.append(request)
        if handler:
            return handler(request, len(calls))
        return httpx.Response(
            200,
            json=quote_body(now)
            if request.url.path.endswith("/quote")
            else intraday_body(request, now),
        )

    config = load_dhan_configuration(
        environ={
            "DHAN_DATA_API_ENABLED": "true",
            "DHAN_ACCESS_TOKEN": TOKEN,
            "DHAN_CLIENT_ID": CLIENT,
        }
    )
    return DhanMarketProvider(
        config, transport_factory=lambda: httpx.MockTransport(respond), clock=lambda: now
    ), calls
