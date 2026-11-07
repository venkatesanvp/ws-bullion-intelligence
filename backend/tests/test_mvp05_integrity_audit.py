"""MVP05 failure-injection tests. Synthetic fixtures only; no network or database."""

from copy import deepcopy
import asyncio
import json
import logging
from uuid import UUID
import httpx
import pytest
from fastapi.testclient import TestClient
from app.errors import APIError
from app.market_cache_transfer import SessionTransfer, export_cache, restore_cache
from .conftest import TOKEN, ORIGIN
from .provider_fixtures import collected
from .test_market_session import setup


def populated():
    old, service, calls, _ = setup()
    plan, result, _ = collected()
    old.state.transient_research.install(
        result,
        plan,
        names={x.symbol: "SYNTHETIC TEST ONLY" for x in service.provider.listings()},
        data_class="SYNTHETIC_TEST",
    )
    service.get_quotes()
    service.intraday(service.daily.store.listings()[0].id, 5, "previous")
    return export_cache(old)


def state(app):
    return json.dumps(export_cache(app), sort_keys=True)


def test_every_value_identity_time_and_provenance_preserved_and_replay_is_safe():
    payload = populated()
    app, service, calls, _ = setup()
    original = deepcopy(payload)
    assert restore_cache(app, SessionTransfer.model_validate(payload))["intraday_candles"] == 75
    after = export_cache(app)
    for key in ("quotes", "candles", "budget_attempts", "budget_day", "daily_attempts"):
        assert after[key] == payload[key]
    for actual, expected in zip(after["daily"]["series"], payload["daily"]["series"]):
        for key in ("isin", "rows", "batch_evidence", "observation_evidence"):
            assert actual[key] == expected[key]
    assert payload == original  # Remapping does not mutate caller-owned evidence.
    snapshot = state(app)
    with pytest.raises(APIError, match="Restore before"):
        restore_cache(app, SessionTransfer.model_validate(payload))
    assert state(app) == snapshot and not calls


@pytest.mark.parametrize(
    "defect",
    [
        "duplicate_daily",
        "duplicate_candle",
        "duplicate_quote",
        "wrong_daily_identity",
        "wrong_candle_identity",
        "timestamp_mismatch",
        "fractional_volume",
        "corrupt_price",
        "bad_duration",
        "invalid_version",
    ],
)
def test_invalid_payload_never_partially_publishes(defect):
    payload = populated()
    if defect == "duplicate_daily":
        series = next(s for s in payload["daily"]["series"] if s["rows"])
        series["rows"].append(deepcopy(series["rows"][0]))
    elif defect == "duplicate_candle":
        payload["candles"].append(deepcopy(payload["candles"][0]))
    elif defect == "duplicate_quote":
        payload["quotes"].append(deepcopy(payload["quotes"][0]))
    elif defect == "wrong_daily_identity":
        payload["daily"]["series"][-1]["isin"] = "INF000000001"
    elif defect == "wrong_candle_identity":
        payload["candles"][0]["listing"]["isin"] = "INF000000001"
    elif defect == "timestamp_mismatch":
        payload["candles"][0]["source_timestamp"] = str(
            int(payload["candles"][0]["source_timestamp"]) + 60
        )
    elif defect == "fractional_volume":
        payload["candles"][0]["volume"] = "1.5"
    elif defect == "corrupt_price":
        payload["daily"]["series"][0]["rows"][0]["close"] = "NaN"
    elif defect == "bad_duration":
        payload["candles"][0]["interval"] = 1
    elif defect == "invalid_version":
        payload["version"] = 7
    app, _, calls, _ = setup()
    before = state(app)
    with pytest.raises((APIError, ValueError)):
        restore_cache(app, SessionTransfer.model_validate(payload))
    assert state(app) == before and not calls
    assert not getattr(app.state.transient_research, "_handoff_sealed", False)


def test_coverage_failure_after_daily_validation_is_atomic_and_retryable(monkeypatch):
    payload = populated()
    app, service, calls, _ = setup()
    before = state(app)
    original = service.expected_starts

    def interrupted(*args):
        raise RuntimeError("synthetic interrupted preparation")

    monkeypatch.setattr(service, "expected_starts", interrupted)
    with pytest.raises(RuntimeError):
        restore_cache(app, SessionTransfer.model_validate(payload))
    assert state(app) == before and not calls
    monkeypatch.setattr(service, "expected_starts", original)
    assert restore_cache(app, SessionTransfer.model_validate(payload))["daily_observations"] > 0


@pytest.mark.parametrize(
    "headers,body,status",
    [
        ({"Authorization": "Bearer " + TOKEN}, None, 403),
        ({"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}, b'{"daily":', 422),
        ({"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}, b"{}", 422),
    ],
)
def test_http_invalid_or_partial_restore_cannot_change_state(headers, body, status):
    app, _, calls, _ = setup()
    before = state(app)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/market-data/cache-transfer",
            content=body or json.dumps(populated()),
            headers={**headers, "Content-Type": "application/json"},
        )
    assert response.status_code == status and state(app) == before and not calls


def test_disconnected_partial_upload_never_reaches_restore():
    app, _, calls, _ = setup()
    before = state(app)

    async def run():
        messages = iter(
            [
                {"type": "http.request", "body": b'{"daily":', "more_body": True},
                {"type": "http.disconnect"},
            ]
        )

        async def receive():
            return next(messages, {"type": "http.disconnect"})

        async def send(message):
            pass

        await app(
            {
                "type": "http",
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/api/v1/market-data/cache-transfer",
                "query_string": b"",
                "headers": [
                    (b"host", b"127.0.0.1"),
                    (b"authorization", ("Bearer " + TOKEN).encode()),
                    (b"origin", ORIGIN.encode()),
                ],
                "client": ("127.0.0.1", 1),
                "server": ("127.0.0.1", 1),
            },
            receive,
            send,
        )

    asyncio.run(run())
    assert state(app) == before and not calls


def test_restore_does_not_call_unavailable_provider(monkeypatch):
    payload = populated()
    app, service, calls, _ = setup()

    def forbidden(*args, **kwargs):
        raise AssertionError("provider unavailable, must not be called")

    monkeypatch.setattr(service.provider, "retrieve_quotes", forbidden)
    monkeypatch.setattr(service.provider, "retrieve_intraday", forbidden)
    assert restore_cache(app, SessionTransfer.model_validate(payload))["quotes"] == 4
    assert not calls


@pytest.mark.parametrize("status", [200, 401, 403, 429, 500])
def test_manual_refresh_failure_audit_has_trigger_correlation_and_zero_retries(status, caplog):
    from .session_fixtures import quote_body, TOKEN as PROVIDER_TOKEN, CLIENT

    app, service, calls, clock = setup(
        handler=lambda r, n: httpx.Response(status, json=quote_body() if status == 200 else {})
    )
    with caplog.at_level(logging.INFO, logger="bullion"), TestClient(app) as client:
        response = client.post(
            "/api/v1/market-data/quotes",
            json={"refresh": True},
            headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN},
        )
    events = [json.loads(r.message) for r in caplog.records if r.message.startswith("{")]
    completed = [e for e in events if e.get("event") == "PROVIDER_OPERATION_COMPLETED"]
    assert len(calls) == 1 and len(completed) == 1
    e = completed[0]
    assert e["trigger"] == "MANUAL_REFRESH" and e["operation"] == "QUOTE" and e["retry_count"] == 0
    assert e["counter_after"] - e["counter_before"] == 1
    assert e["correlation_id"] == response.headers["X-Request-ID"] and UUID(e["correlation_id"])
    assert e["timestamp"] and e["outcome"] == ("SUCCEEDED" if status == 200 else "FAILED")
    assert PROVIDER_TOKEN not in caplog.text and CLIENT not in caplog.text
    if status != 200:
        service.get_quotes(refresh=True)
        assert len(calls) == 1  # circuit blocks, no retry


def test_startup_cached_navigation_never_acquires():
    app, service, calls, _ = setup()
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer " + TOKEN}
        for path in [
            "/health/live",
            "/market-data/policy",
            "/market-data/session-policy",
            "/market-data/cache-transfer",
        ]:
            assert client.get("/api/v1" + path, headers=headers).status_code == 200
    assert not calls


def test_cached_quote_service_never_acquires():
    _, service, calls, _ = setup()
    service.get_quotes(cached_only=True)
    assert not calls


@pytest.mark.parametrize("kind", ["run", "evaluate"])
def test_forecast_and_evaluation_use_snapshot_without_provider(kind):
    from threading import Event
    from .forecast_research_fixtures import service_fixture

    service, reader, body, _, _, _, cal = service_fixture()

    def forbidden(*args, **kwargs):
        raise AssertionError("Unexpected provider call from snapshot-only research")

    service.market.ensure = forbidden
    service.market.provider.retrieve_daily = forbidden
    service.market.provider.retrieve_quotes = forbidden
    if kind == "evaluate":
        body = body.model_copy(
            update={"start": cal.sessions[100].session_date, "end": cal.sessions[130].session_date}
        )
    result = service.work(kind, reader, body, Event())
    assert result["status"] == "AVAILABLE"
