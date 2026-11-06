"""CI-only synthetic backend. Fails closed outside a local disposable test database."""

from datetime import timedelta
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
p = plan(start=NOW.date() - timedelta(days=35), end=NOW.date())
app = create_app(
    settings_for_browser(
        url, market_data_enabled=True, market_quotes_enabled=True, market_intraday_enabled=True
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
