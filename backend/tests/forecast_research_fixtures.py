"""Synthetic canonical records exercising real-source contracts; no market observations."""

from types import SimpleNamespace as NS
from datetime import timedelta
from uuid import uuid5, NAMESPACE_URL
from app.dhan_history_contract import INSTRUMENTS
from app.dhan_provider import _listing
from app.forecast_research_service import ForecastResearchService, ResearchOptions
from app.forecast_contracts import fingerprint
from .forecast_fixtures import dataset


def canonical_input(count=180, *, index=0, real=True):
    base = dataset(count=400, future=150)
    listing = _listing(INSTRUMENTS[index])
    iid = uuid5(NAMESPACE_URL, "mock-forecast:" + listing.isin)
    sid = uuid5(NAMESPACE_URL, "mock-forecast-source")
    instrument = NS(
        id=iid,
        symbol=listing.symbol,
        exchange=listing.exchange,
        currency=listing.currency,
        isin=listing.isin,
        active=True,
    )
    source = NS(
        id=sid,
        source_kind="DHANHQ",
        qualification="TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED",
        contract_version="SYNTHETIC_MOCK_REAL_CONTRACT_ONLY",
        label="SYNTHETIC fixture exercising real contract",
        rights_evidence_ref="SYNTHETIC TEST ONLY - NO REAL DATA RIGHTS CLAIM",
        reviewed_at=base.calendar.known_at,
        permitted_uses={"retrieval": True, "analysis": True, "display": True, "storage": False},
        profile={
            "data_class": "REAL_MARKET" if real else "SYNTHETIC_TEST",
            "calendar": {},
            "known_break_dates": [],
        },
    )
    rows = []
    for p in base.observations[:count]:
        rows.append(
            NS(
                id=uuid5(iid, str(p.session_date)),
                batch_id=uuid5(iid, "batch"),
                row_number=len(rows) + 1,
                canonical_hash=fingerprint(p),
                trading_date=p.session_date,
                interval="1d",
                price_basis="PROVIDER_ADJUSTED",
                open=p.open,
                high=p.high,
                low=p.low,
                close=p.close,
                volume=p.volume,
                ingested_at=p.available_at,
                event_time=None,
                event_precision="DATE_ONLY",
                provider_published_at=None,
            )
        )
    return instrument, source, tuple(rows), base.calendar


def service_fixture(count=180, *, index=0, real=True):
    i, s, rows, cal = canonical_input(count, index=index, real=real)
    ref = [(i, s, rows)]
    clock = [cal.sessions[count - 1].close_at + timedelta(days=1, hours=1)]
    ticks = [0.0]
    listings = tuple(_listing(x) for x in INSTRUMENTS)
    store = NS(listings=lambda: (i,), has_series=lambda a, b: a == i.id and b == s.id)
    market = NS(
        provider=NS(listings=lambda: listings),
        store=store,
        clock=lambda: clock[0],
        public_policy=lambda: {
            "enabled": True,
            "latest_provider_eligible_session_candidate": str(rows[-1].trading_date),
        },
    )
    service = ForecastResearchService(market, calendar_override=cal, monotonic=lambda: ticks[0])
    body = ResearchOptions(instrument_id=i.id, source_id=s.id, horizon=5, lookback=60)
    return service, lambda: ref[0], body, ref, clock, ticks, cal
