"""Authenticated local API integration on synthetic canonical records; no DB/network writes."""

from types import SimpleNamespace as NS
import pytest
from fastapi.testclient import TestClient
from app.main import create_app, get_db
from .conftest import test_settings as settings_for_forecast_api, TOKEN, ORIGIN
from .session_fixtures import provider_for_session
from .forecast_research_fixtures import service_fixture


@pytest.fixture
def forecast_api():
    provider, _ = provider_for_session()
    app = create_app(settings_for_forecast_api(), market_provider=provider)
    s, reader, body, ref, clock, ticks, cal = service_fixture()
    i, source, rows = reader()
    memory = NS(
        has_series=lambda a, b: a == i.id and b == source.id,
        series=lambda a, b: reader()[:2],
        rows=lambda *args: reader()[2],
    )

    def db():
        yield NS(info={"transient_research": memory})

    app.dependency_overrides[get_db] = db
    app.state.forecast_research = s
    with TestClient(app, headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}) as client:
        yield client, app, body, cal


def test_context_run_evaluation_and_tracking_use_existing_auth_and_exact_research_contracts(
    forecast_api,
):
    c, app, b, cal = forecast_api
    params = {"instrument_id": str(b.instrument_id), "source_id": str(b.source_id)}
    context = c.get("/api/v1/research/forecasts/context", params=params)
    assert context.status_code == 200
    data = context.json()["data"]
    assert data["eligible_observations"] == 180 and data["quality"] == "CONDITIONAL_OWNER_RESEARCH"
    run = c.post(
        "/api/v1/research/forecasts/run",
        json={**b.model_dump(mode="json"), "expected_revision": data["revision"]},
    )
    assert run.status_code == 200
    result = run.json()["data"]
    assert result["status"] == "AVAILABLE" and run.headers["cache-control"] == "no-store"
    assert all(
        r["forecast"]["provenance"]["data_class"] == "REAL_MARKET" for r in result["results"]
    )
    assert result["results"][2]["forecast"]["predicted_price"] is None
    track = c.get("/api/v1/research/forecasts/runs/" + result["run_id"])
    assert track.status_code == 200
    assert all(x["status"] == "PENDING" for x in track.json()["data"]["tracking"])
    body = {
        **b.model_dump(mode="json"),
        "start": str(cal.sessions[100].session_date),
        "end": str(cal.sessions[130].session_date),
        "frequency": 5,
    }
    evaluated = c.post("/api/v1/research/forecasts/evaluate", json=body)
    assert evaluated.status_code == 200
    e = evaluated.json()["data"]
    assert e["sample_count"] == 7 and e["experiment"]["classification"] == "STRICT_POINT_IN_TIME"
    assert c.get("/api/v1/research/forecasts/runs").json()["data"]["runs"]


def test_auth_origin_canary_errors_and_body_validation_do_not_expose_credentials(forecast_api):
    c, app, b, _ = forecast_api
    body = b.model_dump(mode="json")
    path = "/api/v1/research/forecasts/run"
    with TestClient(app) as unauth:
        assert unauth.post(path, json=body, headers={"Origin": ORIGIN}).status_code == 401
    assert (
        c.post(path, json=body, headers={"Origin": "http://untrusted.invalid"}).status_code == 403
    )
    canary = "synthetic-canary-never-a-real-provider-secret"
    r = c.post(path, json={**body, "access_token": canary})
    assert r.status_code == 422 and canary not in r.text
    assert c.post(path, json={**body, "lookback": 1001}).status_code == 422
    assert c.post(path, json={**body, "models": ["ORDER_PLACEMENT"]}).status_code == 422
    r = c.post(path, json={**body, "basis": "RAW_CLOSE"})
    assert r.status_code == 422 and "FORECAST_BASIS_NOT_SUPPORTED" in r.text
    app.state.forecast_research._gate.acquire()
    try:
        assert c.post(path, json=body).status_code == 429
    finally:
        app.state.forecast_research._gate.release()
    routes = {path for path in app.openapi()["paths"] if "/research/forecasts" in path}
    assert not any(
        x in path.lower() for path in routes for x in ("order", "trade", "balance", "holdings")
    )


def test_snapshot_change_tracking_absence_and_unavailable_models_are_explicit(forecast_api):
    c, app, b, _ = forecast_api
    body = b.model_dump(mode="json")
    r = c.post("/api/v1/research/forecasts/run", json={**body, "expected_revision": "0" * 64})
    assert r.status_code == 409
    r = c.post("/api/v1/research/forecasts/run", json={**body, "lookback": 1000})
    assert r.status_code == 200 and r.json()["data"]["status"] == "UNAVAILABLE"
    r = c.get("/api/v1/research/forecasts/runs/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_conditional_replay_api_requires_ack_and_returns_unambiguous_mode_evidence(forecast_api):
    c, app, b, cal = forecast_api
    body = {
        **b.model_dump(mode="json"),
        "start": str(cal.sessions[100].session_date),
        "end": str(cal.sessions[110].session_date),
        "evaluation_mode": "CONDITIONAL_HISTORICAL_REPLAY",
    }
    denied = c.post("/api/v1/research/forecasts/evaluate", json=body)
    assert (
        denied.status_code == 422
        and denied.json()["error"]["code"] == "CONDITIONAL_REPLAY_ACKNOWLEDGEMENT_REQUIRED"
    )
    allowed = c.post(
        "/api/v1/research/forecasts/evaluate",
        json={
            **body,
            "acknowledge_replay_assumptions": True,
            "replay_policy": "FIXED_RETRIEVED_VINTAGE_V1",
        },
    )
    assert allowed.status_code == 200 and allowed.headers["cache-control"] == "no-store"
    data = allowed.json()["data"]
    assert (
        data["evaluation_mode"]
        == data["experiment"]["classification"]
        == "CONDITIONAL_HISTORICAL_REPLAY"
    )
    assert data["sample_count"] == 3 and data["assumptions"]
    assert all(row["evaluation_mode"] == data["evaluation_mode"] for row in data["rows"])


def test_evaluation_modes_cannot_be_spoofed_or_echo_secrets(forecast_api):
    c, app, b, cal = forecast_api
    base = {
        **b.model_dump(mode="json"),
        "start": str(cal.sessions[100].session_date),
        "end": str(cal.sessions[110].session_date),
    }
    r = c.post("/api/v1/research/forecasts/evaluate", json={**base, "evaluation_mode": "SYNTHETIC"})
    assert r.status_code == 422 and r.json()["error"]["code"] == "EVALUATION_MODE_SOURCE_MISMATCH"
    canary = "SYNTHETIC_NOT_A_REAL_CREDENTIAL_MODE_CANARY"
    r = c.post("/api/v1/research/forecasts/evaluate", json={**base, "evaluation_mode": canary})
    assert r.status_code == 422 and canary not in r.text
    r = c.post(
        "/api/v1/research/forecasts/evaluate",
        json={
            **base,
            "evaluation_mode": "CONDITIONAL_HISTORICAL_REPLAY",
            "acknowledge_replay_assumptions": "true",
            "replay_policy": "FIXED_RETRIEVED_VINTAGE_V1",
        },
    )
    assert r.status_code == 422


def test_performance_registry_is_authenticated_transient_and_options_bounded(forecast_api):
    c, app, b, cal = forecast_api
    path = "/api/v1/research/forecasts/performance"
    with TestClient(app) as unauth:
        assert unauth.get(path).status_code == 401
    assert c.get(path).json()["data"]["records"] == []
    body = {
        **b.model_dump(mode="json"),
        "start": str(cal.sessions[100].session_date),
        "end": str(cal.sessions[130].session_date),
        "regime_analysis": True,
        "rolling_error_window": 3,
    }
    r = c.post("/api/v1/research/forecasts/evaluate", json=body)
    assert r.status_code == 200
    p = r.json()["data"]["performance"]
    assert p["regime_rule_version"] == "fixed-21-close-v1" and len(p["cards"]) == 3
    reg = c.get(path)
    assert reg.status_code == 200 and reg.headers["cache-control"] == "no-store"
    assert (
        len(reg.json()["data"]["records"]) == 1 and "errors" not in reg.json()["data"]["records"][0]
    )
    for invalid in (
        {"rolling_error_window": 31},
        {"rolling_error_window": 1},
        {"regime_analysis": "true"},
    ):
        assert (
            c.post("/api/v1/research/forecasts/evaluate", json={**body, **invalid}).status_code
            == 422
        )
