"""CI-only synthetic backend. Fails closed outside a local disposable test database."""

from datetime import timedelta, datetime, time as clock_time
from app.forecast_contracts import TradingCalendar, CalendarSession
from app.market_session import IST
from threading import Event
from datetime import timezone
from .test_market_stream import frame
from app.dhan_history_contract import INSTRUMENTS
import time
import os
from sqlalchemy.engine import make_url
from app.main import create_app
from app.provider_budget import ProviderBudget
from app.transient_uat import NAMES
from .conftest import test_settings as settings_for_browser
from .provider_fixtures import collected, plan
from .session_fixtures import provider_for_session, NOW

url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL", "")
parsed = make_url(url)
if parsed.host not in {"127.0.0.1", "localhost"} or not (parsed.database or "").endswith("_test"):
    raise RuntimeError("Disposable local test database required")
provider, _ = provider_for_session()
p = plan(start=NOW.date() - timedelta(days=100), end=NOW.date())
app = create_app(
    settings_for_browser(
        url,
        market_data_enabled=True,
        market_quotes_enabled=True,
        market_intraday_enabled=True,
        market_stream_enabled=True,
    ),
    market_provider=provider,
    market_calendar=p.calendar,
)
_, collection, _ = collected(p)
app.state.transient_research.install(collection, p, names=NAMES, data_class="SYNTHETIC_TEST")
for source in app.state.transient_research.sources():
    source.profile = {**source.profile, "market_session_mock": True}
started = time.monotonic()


def clock():
    return NOW + timedelta(seconds=time.monotonic() - started)


provider.clock = clock
app.state.market_data.clock = clock
app.state.market_session.clock = clock
app.state.market_session.budget = ProviderBudget(clock=clock, pause=lambda _: None)


# CI-only deterministic binary feed. The production connector is never called.


class SyntheticSocket:
    def __init__(self):
        self.packets = [frame(6, sid=int(i.security_id)) for i in INSTRUMENTS]
        self.last = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send(self, message):
        pass

    def recv(self, timeout):
        if self.packets:
            return self.packets.pop(0)
        if time.monotonic() - self.last >= 2:
            self.last = time.monotonic()
            self.packets = [
                frame(
                    sid=int(i.security_id),
                    epoch=int(clock().replace(tzinfo=timezone.utc).timestamp()),
                    value=101.23,
                )
                for i in INSTRUMENTS
            ]
            return self.packets.pop(0)
        time.sleep(0.1)
        raise TimeoutError()

    def ping(self):
        event = Event()
        event.set()
        return event


app.state.market_stream.connector = lambda *args, **kwargs: SyntheticSocket()

# Package 4 explicit synthetic forecast availability/calendar: never real publication evidence.

forecast_days = set(p.calendar.session_dates)
future_day = p.calendar.coverage_end + timedelta(days=1)
forecast_end = p.calendar.coverage_end + timedelta(days=300)
while future_day <= forecast_end:
    if future_day.weekday() < 5:
        forecast_days.add(future_day)
    future_day += timedelta(days=1)
forecast_cal = TradingCalendar(
    calendar_id="SYNTHETIC_BROWSER_NOT_NSE",
    version="synthetic-future-v1",
    timezone="Asia/Kolkata",
    known_at=datetime.combine(p.calendar.coverage_start, clock_time(0), IST) - timedelta(days=1),
    coverage_start=p.calendar.coverage_start,
    coverage_end=forecast_end,
    sessions=tuple(
        CalendarSession(session_date=d, close_at=datetime.combine(d, clock_time(15, 30), IST))
        for d in sorted(forecast_days)
    ),
)
app.state.forecast_research.calendar_override = forecast_cal
for entry in app.state.transient_research._datasets.values():
    entry["source"].reviewed_at = forecast_cal.known_at
    for observation in entry["rows"]:
        observation.ingested_at = datetime.combine(
            observation.trading_date, clock_time(15, 50), IST
        )
