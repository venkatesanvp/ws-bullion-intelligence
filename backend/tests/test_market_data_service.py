"""Offline synthetic acquisition/coverage tests. No live provider calls."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from threading import Event
import json

import httpx
import pytest
from app.config import Settings
from app.market_data_service import MarketDataService
from app.transient_research import TransientResearch
from .provider_fixtures import plan, provider_for, body_for


def setup(*, handler=None, missing=(), **policy):
    p = plan(date(2026, 10, 26), date(2026, 11, 6))
    provider, calls = provider_for(p, handler=handler, missing=missing)
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://test:test@127.0.0.1/unavailable_test",
        local_app_token="synthetic-application-token-no-real-secret",
        market_data_enabled=True,
        market_data_min_interval_seconds=0.2,
        **policy,
    )
    store = TransientResearch()
    store.configure(provider.listings(), p.calendar, data_class="SYNTHETIC_TEST")
    clock = [datetime(2026, 11, 6, 7, tzinfo=timezone.utc)]
    service = MarketDataService(provider, store, settings, p.calendar, clock=lambda: clock[0])
    instrument, source = store.listings()[0], store.sources()[0]

    def ensure(start=date(2026, 10, 26), end=date(2026, 10, 30), **kw):
        return service.ensure(instrument.id, source.id, start, end, **kw)

    return service, store, calls, clock, ensure, p


def test_missing_then_reuse_and_exact_decimal_provenance():
    service, store, calls, _, ensure, _ = setup()
    result = ensure()
    assert result["added"] == 5 and result["requests"] == 1
    assert ensure()["status"] == "REUSED" and len(calls) == 1
    instrument, source = store.listings()[0], store.sources()[0]
    rows = store.rows(instrument.id, source.id, "PROVIDER_ADJUSTED")
    assert all(type(r.close) is Decimal for r in rows)
    assert len({r.trading_date for r in rows}) == 5
    evidence = store._datasets[(instrument.id, source.id)]["provenance"][0]
    assert evidence["observation_provenance"][0].source_timestamp
    assert evidence["summary"]["provenance"]["timestamp_semantics_verified"] is False
    assert service.public_policy()["max_concurrent_provider_requests"] == 1


def test_middle_gaps_fetch_only_missing_ranges():
    _, _, calls, _, ensure, _ = setup()
    ensure(date(2026, 10, 26), date(2026, 10, 26))
    ensure(date(2026, 10, 28), date(2026, 10, 28))
    result = ensure()
    requested = [json.loads(r.content) for r in calls[2:]]
    assert [(r["fromDate"], r["toDate"]) for r in requested] == [
        ("2026-10-27", "2026-10-28"),
        ("2026-10-29", "2026-10-31"),
    ]
    assert result["added"] == 3 and result["dataset_count"] == 5


def test_holiday_pending_future_are_not_provider_requests():
    _, _, calls, _, ensure, _ = setup()
    result = ensure(date(2026, 10, 31), date(2026, 11, 8))
    assert result["coverage"]["NON_TRADING"] == 2
    assert result["coverage"]["PROVIDER_PENDING"] == 3  # Nov 6 + future unassessed days
    assert json.loads(calls[0].content)["toDate"] == "2026-11-06"
    assert result["latest_provider_eligible_session_candidate"] == "2026-11-05"


@pytest.mark.parametrize(
    "missing", [tuple(date(2026, 10, d) for d in range(26, 31)), (date(2026, 10, 28),)]
)
def test_empty_partial_and_negative_cache_do_not_claim_holiday(missing):
    _, _, calls, clock, ensure, _ = setup(missing=missing)
    result = ensure()
    assert result["status"] == "PARTIAL"
    assert result["coverage"]["ATTEMPTED_EMPTY"] == len(missing)
    ensure()
    assert len(calls) == 1
    clock[0] += timedelta(hours=2)
    ensure()
    assert len(calls) == 2


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "AUTH_INVALID_OR_EXPIRED"),
        (403, "ACCESS_DENIED"),
        (429, "RATE_LIMITED"),
        (500, "PROVIDER_SERVICE_ERROR"),
    ],
)
def test_provider_errors_stop_without_retries_or_data_loss(status, code):
    count = [0]

    def handler(r, n):
        count[0] += 1
        if n == 1:
            return httpx.Response(
                200, content=body_for(r, p.calendar), headers={"Content-Type": "application/json"}
            )
        return httpx.Response(status, content=b"{}", headers={"Content-Type": "application/json"})

    _, store, calls, clock, ensure, p = setup(handler=handler)
    ensure()
    before = store.rows(store.listings()[0].id, store.sources()[0].id, "PROVIDER_ADJUSTED")
    result = ensure(date(2026, 11, 2), date(2026, 11, 5))
    assert result["error"] == code and result["requests"] == 1
    assert result["coverage"]["FAILED"] == 4
    assert store.rows(store.listings()[0].id, store.sources()[0].id, "PROVIDER_ADJUSTED") == before
    ensure(date(2026, 11, 2), date(2026, 11, 5))
    assert len(calls) == 2
    clock[0] += timedelta(minutes=6)
    ensure(date(2026, 11, 2), date(2026, 11, 5))
    assert len(calls) == 3


def test_timeout_and_cancellation():
    def timeout(r, n):
        raise httpx.ReadTimeout("synthetic secret must never escape", request=r)

    _, _, calls, _, ensure, _ = setup(handler=timeout)
    assert ensure()["error"] == "NETWORK_TIMEOUT"
    cancelled = Event()
    cancelled.set()
    assert ensure(cancel=cancelled)["status"] == "CANCELLED"
    assert len(calls) == 1


def test_cancellation_after_transport_prevents_publication():
    cancel = Event()

    def handler(r, n):
        cancel.set()
        return httpx.Response(
            200, content=body_for(r, p.calendar), headers={"Content-Type": "application/json"}
        )

    _, store, calls, _, ensure, p = setup(handler=handler)
    result = ensure(cancel=cancel)
    assert result["status"] == "CANCELLED" and len(calls) == 1
    assert not store.rows(store.listings()[0].id, store.sources()[0].id, "PROVIDER_ADJUSTED")


def test_concurrent_duplicate_requests_are_single_flight():
    _, _, calls, _, ensure, _ = setup()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: ensure(), range(4)))
    assert len(calls) == 1
    assert sum(r["requests"] for r in results) == 1


def test_inception_and_unknown_calendar_never_infer_closure():
    service, store, calls, _, ensure, _ = setup()
    service.availability[store.listings()[0].isin] = date(2026, 10, 28)
    result = ensure()
    assert result["coverage"]["OUTSIDE_VERIFIED_HISTORY"] == 2
    assert json.loads(calls[0].content)["fromDate"] == "2026-10-28"
    assert service.session(date(2025, 1, 4)) is None


def test_bounded_partition_request_budget_and_disable():
    _, _, calls, _, ensure, _ = setup(market_data_partition_days=2, market_data_max_requests=1)
    result = ensure()
    assert len(calls) == 1 and result["coverage"]["NOT_REQUESTED"] == 3
    service, _, calls, _, ensure, _ = setup()
    service.policy.market_data_enabled = False
    assert ensure()["error"] == "MARKET_DATA_DISABLED" and not calls


def test_refresh_revision_and_duplicate_identity():
    _, store, calls, _, ensure, _ = setup()
    ensure()
    first = store.rows(store.listings()[0].id, store.sources()[0].id, "PROVIDER_ADJUSTED")
    result = ensure(refresh=True)
    assert result["requests"] == 1 and result["added"] == 0
    assert store.rows(store.listings()[0].id, store.sources()[0].id, "PROVIDER_ADJUSTED") == first
    assert len(calls) == 2


def test_staleness_and_warmup_are_bounded():
    _, _, calls, clock, ensure, _ = setup()
    ensure()
    clock[0] += timedelta(days=8)
    assert ensure()["requests"] == 1
    result = ensure(date(2026, 11, 2), date(2026, 11, 5), warmup_bars=5)
    assert result["acquisition_start"] == "2026-10-26"
    assert result["warmup_available"] == 5 and result["warmup_complete"]
    assert len(calls) == 3


@pytest.mark.parametrize("defect", ["fractional_volume", "ohlc", "duplicate", "malformed"])
def test_invalid_payload_is_rejected_and_sanitized(defect):
    def handler(r, n):
        body = json.loads(body_for(r, p.calendar))
        if defect == "fractional_volume":
            body["volume"][0] = 1.5
        if defect == "ohlc":
            body["low"][0] = 99999
        if defect == "duplicate":
            body["timestamp"][1] = body["timestamp"][0]
        if defect == "malformed":
            body.pop("close")
        return httpx.Response(200, json=body)

    _, store, _, _, ensure, p = setup(handler=handler)
    result = ensure()
    assert result["coverage"]["REJECTED"] == 5
    assert result["added"] == 0
    assert not store.rows(store.listings()[0].id, store.sources()[0].id, "PROVIDER_ADJUSTED")
    assert "access-token" not in json.dumps(result)


def test_capacity_guard_preserves_existing_rows():
    _, store, _, _, ensure, _ = setup()
    ensure()
    service = setup()[0]
    service.policy.market_data_max_rows = 1
    # Shared merge is the final authoritative capacity gate (regardless of planner).
    from app.acquisition import CollectedSeries
    from app.market_data import DailyRequest

    result = service.provider.retrieve_daily(
        DailyRequest(
            service.provider.listings()[0], date(2026, 10, 26), date(2026, 10, 30), service.calendar
        ),
        request_approved=True,
    )
    collected = CollectedSeries(
        service.provider.listings()[0],
        date(2026, 10, 26),
        date(2026, 10, 30),
        "synthetic",
        (result,),
    )
    with pytest.raises(Exception):
        service.store.merge(
            service.store.listings()[0].id, service.store.sources()[0].id, collected, max_rows=1
        )
    assert len(store.rows(store.listings()[0].id, store.sources()[0].id, "PROVIDER_ADJUSTED")) == 5


def test_application_route_auth_sanitization_and_normal_startup_without_credentials(caplog):
    from fastapi.testclient import TestClient
    from app.main import create_app
    from .conftest import test_settings, TOKEN, ORIGIN

    p = plan(date(2026, 10, 26), date(2026, 10, 30))
    provider, calls = provider_for(p)
    app = create_app(
        test_settings(market_data_enabled=True),
        market_provider=provider,
        market_calendar=p.calendar,
    )
    store = app.state.transient_research
    body = {
        "instrument_id": str(store.listings()[0].id),
        "source_id": str(store.sources()[0].id),
        "start": "2026-10-26",
        "end": "2026-10-30",
    }
    with TestClient(app) as client:
        assert client.post("/api/v1/market-data/ensure", json=body).status_code == 401
        assert not calls
        headers = {"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}
        response = client.post("/api/v1/market-data/ensure", json=body, headers=headers)
        assert response.status_code == 200 and response.json()["data"]["added"] == 5
        assert (
            client.post("/api/v1/market-data/ensure", json=body, headers=headers).json()["data"][
                "requests"
            ]
            == 0
        )
        assert len(calls) == 1
        safe = response.text + caplog.text
        assert "synthetic-acquisition-token-not-a-credential" not in safe
        assert '"close"' not in response.text
        assert (
            client.post(
                "/api/v1/market-data/ensure",
                json={**body, "start": "garbage-secret"},
                headers=headers,
            ).status_code
            == 422
        )
        assert client.get("/api/v1/health/live").status_code == 200


def test_read_snapshot_and_revision_replacement_are_coherent():
    _, store, _, _, ensure, _ = setup()
    ensure(date(2026, 10, 26), date(2026, 10, 26))
    snapshot = store.snapshot()
    instrument, source = snapshot.listings()[0], snapshot.sources()[0]
    revision = instrument.data_revision
    ensure()
    assert instrument.data_revision == revision
    assert len(snapshot.rows(instrument.id, source.id, "PROVIDER_ADJUSTED")) == 1
    assert len(store.rows(instrument.id, source.id, "PROVIDER_ADJUSTED")) == 5
    assert store.listings()[0].data_revision > revision


def test_handoff_exact_canonical_values_ids_and_once_only():
    from app.transient_handoff import Handoff, restore_canonical_view
    from app.serialization import plain
    from app.errors import APIError

    _, old, _, _, ensure, _ = setup()
    ensure()
    target = TransientResearch()
    source = old.sources()[0]
    from app.schemas import CalendarProfile

    target.configure(
        [setup()[0].provider.listings()[0]],
        CalendarProfile.model_validate(source.profile["calendar"]),
        data_class="SYNTHETIC_TEST",
    )
    old_key = (old.listings()[0].id, source.id)
    rows = old.rows(*old_key, "PROVIDER_ADJUSTED")
    fields = (
        "id",
        "batch_id",
        "row_number",
        "trading_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ingested_at",
        "event_time",
        "event_precision",
        "provider_published_at",
    )
    provenance = old._datasets[old_key]["provenance"][0]["summary"]["provenance"]
    body = Handoff.model_validate(
        {
            "series": [
                {
                    "instrument_id": target.listings()[0].id,
                    "source_id": target.sources()[0].id,
                    "isin": target.listings()[0].isin,
                    "rows": [{k: plain(getattr(r, k)) for k in fields} for r in rows],
                    "batch_evidence": [provenance],
                }
            ]
        }
    )
    assert restore_canonical_view(target, body, 100000)["observations"] == 5
    restored = target.rows(target.listings()[0].id, target.sources()[0].id, "PROVIDER_ADJUSTED")
    assert [r.canonical_hash for r in restored] == [r.canonical_hash for r in rows]
    assert [r.id for r in restored] == [r.id for r in rows]
    assert "ORIGINAL_NUMERIC_EPOCH_NOT_EXPORTED" in str(target.sources()[0].profile)
    with pytest.raises(APIError):
        restore_canonical_view(target, body, 100000)


def test_warmup_does_not_claim_complete_across_a_missing_session():
    _, _, _, _, ensure, _ = setup(missing=(date(2026, 10, 28),))
    result = ensure(date(2026, 11, 2), date(2026, 11, 5), warmup_bars=5)
    assert result["warmup_complete"] is False
    assert result["warmup_available"] == 4


def test_history_uses_same_snapshot_for_metadata_and_rows(api, db_engine, monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import create_app
    from app import main
    from .conftest import test_settings, TOKEN, ORIGIN

    p = plan(date(2026, 10, 26), date(2026, 10, 30))
    provider, _ = provider_for(p)
    app = create_app(
        test_settings(
            db_engine.url.render_as_string(hide_password=False), market_data_enabled=True
        ),
        market_provider=provider,
        market_calendar=p.calendar,
    )
    store = app.state.transient_research
    instrument, source = store.listings()[0], store.sources()[0]
    service = app.state.market_data
    service.ensure(instrument.id, source.id, date(2026, 10, 26), date(2026, 10, 26))
    original = main.series_meta

    def concurrent_merge(*args, **kwargs):
        meta = original(*args, **kwargs)
        service.ensure(instrument.id, source.id, date(2026, 10, 26), date(2026, 10, 30))
        return meta

    monkeypatch.setattr(main, "series_meta", concurrent_merge)
    with TestClient(app, headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}) as client:
        result = client.get(
            f"/api/v1/instruments/{instrument.id}/history?source_id={source.id}&basis=PROVIDER_ADJUSTED"
        ).json()
    assert result["meta"]["coverage"]["count"] == 1
    assert len(result["data"]) == 1
    assert len(store.rows(instrument.id, source.id, "PROVIDER_ADJUSTED")) == 5
