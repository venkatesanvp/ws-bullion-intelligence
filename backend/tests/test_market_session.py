"""Step 5E P0 deterministic synthetic quote/intraday tests; no provider network."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
from threading import Event
import json
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.provider_budget import ProviderBudget
from app.dhan_market_provider import financial, quote_time
from .conftest import test_settings as settings_for_session, TOKEN as APP_TOKEN, ORIGIN
from .provider_fixtures import plan
from .session_fixtures import provider_for_session, quote_body, intraday_body, NOW, TOKEN, CLIENT


def setup(*, handler=None, **settings):
    provider, calls = provider_for_session(handler=handler)
    calendar = plan(date(2026, 10, 1), date(2026, 11, 6)).calendar
    config = settings_for_session(
        market_data_enabled=True,
        market_quotes_enabled=True,
        market_intraday_enabled=True,
        **settings,
    )
    app = create_app(config, market_provider=provider, market_calendar=calendar)
    clock = [NOW]
    service = app.state.market_session
    service.clock = lambda: clock[0]
    app.state.market_data.clock = lambda: clock[0]
    service.budget = ProviderBudget(clock=lambda: clock[0], pause=lambda _: None)
    return app, service, calls, clock


def test_batched_quote_authentication_exact_previous_close_and_cache(caplog):
    _, service, calls, _ = setup()
    result = service.get_quotes()
    assert len(result["quotes"]) == 4 and len(calls) == 1
    request = calls[0]
    assert request.headers["access-token"] == TOKEN and request.headers["client-id"] == CLIENT
    assert json.loads(request.content) == {"NSE_EQ": [21401, 21428, 14428, 8080]}
    quote = result["quotes"][0]
    assert quote["last_price"] == Decimal(101) and quote["previous_close"] == Decimal(100)
    assert quote["percent_change"] == "1.000000000000" and quote["freshness"] == "FRESH"
    assert service.get_quotes()["quotes"] and len(calls) == 1
    service.get_quotes(refresh=True)
    assert len(calls) == 2
    assert TOKEN not in caplog.text and CLIENT not in caplog.text


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "AUTH_INVALID_OR_EXPIRED"),
        (403, "ACCESS_DENIED"),
        (429, "RATE_LIMITED"),
        (500, "PROVIDER_SERVICE_ERROR"),
    ],
)
def test_quote_errors_preserve_valid_cache_and_stop_retry(status, code):
    def handler(request, n):
        return httpx.Response(200, json=quote_body()) if n == 1 else httpx.Response(status, json={})

    _, service, calls, clock = setup(handler=handler)
    before = service.get_quotes()["quotes"]
    clock[0] += timedelta(seconds=16)
    result = service.get_quotes()
    assert (
        result["error"] == code and result["quotes"][0]["retrieved_at"] == before[0]["retrieved_at"]
    )
    service.get_quotes(refresh=True)
    assert len(calls) == 2


def test_timeout_no_secret_exposure():
    def handler(r, n):
        raise httpx.ReadTimeout("private test token " + TOKEN, request=r)

    _, service, calls, _ = setup(handler=handler)
    result = service.get_quotes()
    assert result["error"] == "NETWORK_TIMEOUT" and len(calls) == 1
    assert TOKEN not in str(result)


@pytest.mark.parametrize(
    "defect", ["missing", "negative", "fractional_volume", "bad_time", "previous_close_conflict"]
)
def test_partial_quote_fields_and_ambiguity(defect):
    def handler(r, n):
        body = quote_body()
        q = body["data"]["NSE_EQ"]["21401"]
        if defect == "missing":
            body["data"]["NSE_EQ"].pop("21401")
        if defect == "negative":
            q["last_price"] = -1
        if defect == "fractional_volume":
            q["volume"] = 1.5
        if defect == "bad_time":
            q["last_trade_time"] = "credential " + TOKEN
        if defect == "previous_close_conflict":
            q["ohlc"]["close"] = 95
        return httpx.Response(200, json=body)

    _, service, _, _ = setup(handler=handler)
    result = service.get_quotes()
    first = result["quotes"][0]
    if defect in {"missing", "negative", "fractional_volume"}:
        assert first["freshness"] == "UNAVAILABLE"
    elif defect == "bad_time":
        assert first["last_trade_at"] is None and first["freshness"] == "UNASSESSED"
    else:
        assert (
            first["previous_close"] == Decimal(100)
            and first["previous_close_basis"] == "DERIVED_FROM_DOCUMENTED_NET_CHANGE"
        )
        assert any("PROVIDER_CLOSE_DIFFERS" in w for w in first["warnings"])
    assert TOKEN not in str(result)


def test_stale_quote_market_closed_and_no_continuous_provider_polling():
    _, service, calls, clock = setup()
    service.get_quotes()
    clock[0] += timedelta(seconds=90)
    assert service.get_quotes()["quotes"][0]["freshness"] == "STALE"
    clock[0] = NOW.replace(hour=16)
    for _ in range(3):
        assert service.get_quotes()["policy"]["auto_quote_refresh_seconds"] == 0
    assert len(calls) == 2
    service.get_quotes(refresh=True)
    assert len(calls) == 3


def test_concurrent_quote_batch_is_single_flight():
    _, service, calls, _ = setup()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: service.get_quotes(), range(4)))
    assert len(calls) == 1 and all(len(r["quotes"]) == 4 for r in results)


@pytest.mark.parametrize("interval", [1, 5, 15, 25, 60])
def test_intraday_intervals_midnight_bounds_exact_decimal_and_reuse(interval):
    _, service, calls, _ = setup()
    instrument = service.daily.store.listings()[0]
    result = service.intraday(instrument.id, interval, "previous")
    assert result["status"] == "AVAILABLE" and result["candles"]
    assert result["candles"][0]["start"].hour == 9 and result["candles"][0]["start"].minute == 15
    assert all(type(r["close"]) is Decimal for r in result["candles"])
    request = json.loads(calls[0].content)
    assert (
        request["fromDate"] == "2026-11-05 00:00:00" and request["toDate"] == "2026-11-06 00:00:00"
    )
    assert request["instrument"] == "EQUITY" and request["oi"] is False
    service.intraday(instrument.id, interval, "previous")
    assert len(calls) == 1


@pytest.mark.parametrize(
    "defect",
    ["duplicate", "fractional_timestamp", "negative_volume", "ohlc", "length", "millisecond"],
)
def test_intraday_rejects_malformed_or_inconsistent_data(defect):
    def handler(request, n):
        body = intraday_body(request)
        if defect == "duplicate":
            body["timestamp"][1] = body["timestamp"][0]
        if defect == "fractional_timestamp":
            body["timestamp"][0] += 0.5
        if defect == "negative_volume":
            body["volume"][0] = -1
        if defect == "ohlc":
            body["low"][0] = 999
        if defect == "length":
            body["open"].pop()
        if defect == "millisecond":
            body["timestamp"] = [x * 1000 for x in body["timestamp"]]
        return httpx.Response(200, json=body)

    _, service, calls, _ = setup(handler=handler)
    instrument = service.daily.store.listings()[0]
    result = service.intraday(instrument.id, 5, "previous")
    assert result["error"] == "INVALID_INTRADAY_DATA" and not result["candles"] and len(calls) == 1


def test_intraday_warmup_timeframe_indicators_and_provisional_session_separation():
    _, service, calls, _ = setup()
    instrument = service.daily.store.listings()[0]
    result = service.intraday(
        instrument.id, 5, "current", indicators={"SMA": 200, "EMA": 37, "RSI": 14}
    )
    assert result["warmup_bars"] >= 200
    assert result["indicators"]["SMA"]["timeframe"] == "5m"
    assert any(v["value"] is not None for v in result["indicators"]["SMA"]["values"])
    assert result["provisional_session"]["classification"] == "PROVISIONAL - INTRADAY AGGREGATED"
    assert any(r["classification"] == "INTRADAY_PROVISIONAL" for r in result["candles"])
    provisional = {
        r["start"] for r in result["candles"] if r["classification"] == "INTRADAY_PROVISIONAL"
    }
    assert not provisional & {v["candle_start"] for v in result["indicators"]["SMA"]["values"]}
    assert (
        service.daily.store.rows(
            instrument.id, service.daily.store.sources()[0].id, "PROVIDER_ADJUSTED"
        )
        == ()
    )
    assert len(calls) <= 2


def test_intraday_empty_missing_negative_cache_cancel_and_limits():
    def handler(r, n):
        return httpx.Response(
            200, json={k: [] for k in ["open", "high", "low", "close", "volume", "timestamp"]}
        )

    _, service, calls, _ = setup(
        handler=handler, market_intraday_partition_days=1, market_session_max_requests=1
    )
    instrument = service.daily.store.listings()[0]
    cancel = Event()
    cancel.set()
    assert (
        service.intraday(instrument.id, 5, "previous", cancel=cancel)["error"] == "CANCELLED"
        and not calls
    )
    result = service.intraday(instrument.id, 5, "previous")
    assert result["missing_completed_candles"] == 75 and len(calls) == 1
    service.intraday(instrument.id, 5, "previous")
    assert len(calls) == 1
    result = service.intraday(instrument.id, 5, "five")
    assert result["requests"] == 1


def test_auth_route_validation_and_sanitized_responses(caplog):
    app, service, calls, _ = setup()
    with TestClient(app) as client:
        assert client.post("/api/v1/market-data/quotes", json={}).status_code == 401
        headers = {"Authorization": "Bearer " + APP_TOKEN, "Origin": ORIGIN}
        result = client.post("/api/v1/market-data/quotes", json={}, headers=headers)
        assert result.status_code == 200 and len(result.json()["data"]["quotes"]) == 4
        assert TOKEN not in result.text + caplog.text and CLIENT not in result.text + caplog.text
        body = {
            "instrument_id": str(service.daily.store.listings()[0].id),
            "interval": 5,
            "preset": "previous",
        }
        response = client.post("/api/v1/market-data/intraday", json=body, headers=headers)
        assert response.status_code == 200 and len(response.json()["data"]["candles"]) == 75
        assert (
            client.post(
                "/api/v1/market-data/intraday", json={**body, "interval": True}, headers=headers
            ).status_code
            == 422
        )
        assert client.get("/api/v1/health/live").status_code == 200


def test_disabled_capabilities_and_missing_credentials_make_zero_calls():
    _, service, calls, _ = setup()
    service.settings.market_quotes_enabled = False
    service.settings.market_intraday_enabled = False
    assert service.get_quotes()["error"] == "MARKET_QUOTES_DISABLED"
    instrument = service.daily.store.listings()[0]
    assert service.intraday(instrument.id, 5, "previous")["error"] == "MARKET_INTRADAY_DISABLED"
    assert not calls


def test_decimal_input_precision_and_no_binary_price_conversion():
    assert financial(Decimal("101.1234567890")) == Decimal("101.1234567890")
    for value in [True, 1.1, Decimal("NaN"), Decimal("Infinity"), Decimal("-1")]:
        with pytest.raises((ValueError, ArithmeticError)):
            financial(value)
    assert quote_time("01/01/1980 00:00:00", NOW) is None


def test_cache_transfer_preserves_quotes_intraday_decimal_provenance_and_is_once_only():
    from app.market_cache_transfer import export_cache, restore_cache, SessionTransfer
    from app.errors import APIError

    old, service, _, _ = setup()
    service.get_quotes()
    instrument = service.daily.store.listings()[0]
    service.intraday(instrument.id, 5, "previous")
    exported = export_cache(old)
    fresh, target, _, _ = setup()
    result = restore_cache(fresh, SessionTransfer.model_validate(exported))
    assert result["quotes"] == 4 and result["intraday_candles"] == 75
    assert target.quotes == service.quotes and target.candles == service.candles
    assert target.quote_attempts == service.quote_attempts
    with pytest.raises(APIError):
        restore_cache(fresh, SessionTransfer.model_validate(exported))


def test_cache_transfer_rejects_binary_float_price_and_preserves_empty_target():
    from app.market_cache_transfer import export_cache, restore_cache, SessionTransfer
    from app.errors import APIError

    old, service, _, _ = setup()
    service.get_quotes()
    body = export_cache(old)
    body["quotes"][0]["last_price"] = 101.1
    fresh, target, _, _ = setup()
    with pytest.raises(APIError):
        restore_cache(fresh, SessionTransfer.model_validate(body))
    assert not target.quotes and not target.candles


def test_concurrent_intraday_requests_reuse_one_provider_result():
    _, service, calls, _ = setup()
    instrument = service.daily.store.listings()[0]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda _: service.intraday(instrument.id, 5, "previous"), range(3)))
    assert len(calls) == 1 and all(len(r["candles"]) == 75 for r in results)


def test_intraday_coverage_metadata_capacity_is_bounded():
    from app.errors import APIError

    _, service, calls, _ = setup()
    instrument = service.daily.store.listings()[0]
    service.settings.market_data_max_coverage_days = 1
    with pytest.raises(APIError):
        service.intraday(instrument.id, 5, "five")
    assert not calls and not service.coverage
