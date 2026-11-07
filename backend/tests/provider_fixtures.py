"""Synthetic provider fixtures only; never real market observations or rights evidence."""

from datetime import date, timedelta
from uuid import uuid4
import json

import httpx

from app.acquisition import HistoryPlan, collect_history
from app.dhan_config import load_dhan_configuration
from app.dhan_provider import DhanDailyProvider
from app.models import DataSource, Instrument, now
from app.schemas import CanonicalImportMetadata

TOKEN = "synthetic-acquisition-token-not-a-credential"


def plan(start=date(2025, 11, 2), end=date(2026, 11, 2), **overrides):
    sessions = [
        start + timedelta(days=n)
        for n in range((end - start).days + 1)
        if (start + timedelta(days=n)).weekday() < 5
    ]
    return HistoryPlan(
        start=start,
        end=end,
        calendar={
            "version": "synthetic-weekdays-v1",
            "evidence_ref": "SYNTHETIC weekday fixture, not NSE evidence",
            "coverage_start": start,
            "coverage_end": end,
            "session_dates": sessions,
        },
        **overrides,
    )


def body_for(request, calendar, *, missing=(), change=None):
    body = json.loads(request.content)
    start, end = date.fromisoformat(body["fromDate"]), date.fromisoformat(body["toDate"])
    days = [d for d in calendar.session_dates if start <= d < end and d not in missing]
    epoch = date(1970, 1, 1)
    data = {
        "open": [100 + n for n in range(len(days))],
        "high": [103 + n for n in range(len(days))],
        "low": [99 + n for n in range(len(days))],
        "close": [101 + n for n in range(len(days))],
        "volume": [1000] * len(days),
        "timestamp": [(d - epoch).days * 86400 for d in days],
    }
    if change:
        change(data)
    # Explicit integral-decimal numeric encoding, with no float financial calculation.
    text = json.dumps(data).replace(
        '"volume": ' + json.dumps(data["volume"]),
        '"volume": ['
        + ", ".join(str(v) + ".0" if type(v) is int else json.dumps(v) for v in data["volume"])
        + "]",
    )
    return text.encode()


def provider_for(p, *, handler=None, missing=(), change=None):
    calls = []

    def respond(r):
        calls.append(r)
        if handler:
            return handler(r, len(calls))
        return httpx.Response(
            200,
            content=body_for(r, p.calendar, missing=missing, change=change),
            headers={"Content-Type": "application/json"},
        )

    config = load_dhan_configuration(
        environ={"DHAN_ACCESS_TOKEN": TOKEN, "DHAN_DATA_API_ENABLED": "true"}
    )
    return DhanDailyProvider(config, transport_factory=lambda: httpx.MockTransport(respond)), calls


def collected(p=None, **options):
    p = p or plan()
    provider, calls = provider_for(p, **options)
    result = collect_history(provider, p, request_approved=True, pause=lambda _: None)
    assert result.status == "COLLECTED_UNQUALIFIED"
    return p, result, calls


def register(db, series, p, *, rights=True):
    source = DataSource(
        label="SYNTHETIC provider fixture " + str(uuid4()),
        source_kind="DHANHQ",
        contract_version="dhan-daily-v1-provisional",
        qualification="QUALIFIED_FOR_RESEARCH" if rights else "UNVERIFIED",
        rights_evidence_ref="SYNTHETIC TEST RIGHTS ONLY" if rights else None,
        reviewed_at=now() if rights else None,
        permitted_uses={
            **dict.fromkeys(("retrieval", "storage", "analysis", "display"), rights),
            "retention_review_ref": "SYNTHETIC DISPOSABLE TEST DATABASE" if rights else None,
        },
        profile={
            "data_class": "SYNTHETIC_TEST",
            "policy_version": "quality-v1",
            "calendar": p.calendar.model_dump(mode="json"),
            "adjustment_definition_ref": "SYNTHETIC fixture identity adjustment, not an ETF fact",
            "acquisition_review": {
                "timestamp_policy": "UNIX_SECONDS_IST_CANDIDATE_V1",
                "allow_provisional_session_dates": True,
                "review_ref": "SYNTHETIC TEST POLICY ONLY",
            },
        },
    )
    with db.begin():
        db.add(source)
        instruments = []
        for item in series:
            listing = item.listing
            instrument = Instrument(
                exchange=listing.exchange,
                symbol=listing.symbol,
                isin=listing.isin,
                name="SYNTHETIC " + listing.symbol + " fixture, not market data",
                metal=listing.metal,
                currency=listing.currency,
            )
            db.add(instrument)
            instruments.append(instrument)
        db.flush()
        result = (source.id, [i.id for i in instruments])
    return result


def metadata(series, source_id, instrument_id):
    return CanonicalImportMetadata(
        source_id=source_id,
        instrument_id=instrument_id,
        qualification_ref="SYNTHETIC TEST RIGHTS ONLY",
        plan_fingerprint=series.plan_fingerprint,
        requested_start=series.requested_start,
        requested_end=series.requested_end,
    )
