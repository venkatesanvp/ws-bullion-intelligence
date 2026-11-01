"""VS01-T-19/20/21; local access boundary independent of PostgreSQL."""

from app.main import get_db
from .conftest import ORIGIN, TOKEN


def test_public_liveness_and_protected_readiness(api_no_db):
    live = api_no_db.get("/api/v1/health/live")
    assert live.status_code == 200 and live.json()["data"] == {"status": "alive"}
    assert api_no_db.get("/api/v1/health/ready").status_code == 401
    ready = api_no_db.get("/api/v1/health/ready", headers={"Authorization": "Bearer " + TOKEN})
    assert ready.status_code == 503
    assert ready.json()["error"]["code"] == "DEPENDENCY_NOT_READY"


def test_origin_host_and_wrong_token(api_no_db):
    path = "/api/v1/instruments"
    assert (
        api_no_db.post(path, json={}, headers={"Authorization": "Bearer " + TOKEN}).status_code
        == 403
    )
    assert (
        api_no_db.post(
            path,
            json={},
            headers={"Origin": "https://attacker.invalid", "Authorization": "Bearer " + TOKEN},
        ).status_code
        == 403
    )
    assert api_no_db.get(path, headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert (
        api_no_db.get("/api/v1/health/live", headers={"Host": "attacker.invalid"}).status_code
        == 400
    )
    valid = api_no_db.options(
        path,
        headers={
            "Origin": ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        },
    )
    assert valid.status_code == 200 and valid.headers["access-control-allow-origin"] == ORIGIN
    denied = api_no_db.options(
        path,
        headers={"Origin": "https://attacker.invalid", "Access-Control-Request-Method": "POST"},
    )
    assert denied.status_code == 400 and "access-control-allow-origin" not in denied.headers


def test_body_bound_before_database(api_no_db):
    result = api_no_db.post(
        "/api/v1/import-batches",
        content=b"x" * (1024 + 65537),
        headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN},
    )
    assert result.status_code == 413
    assert result.headers["cache-control"] == "no-store"


def test_malformed_input_does_not_echo_value(api_no_db):
    api_no_db.app.dependency_overrides[get_db] = lambda: None
    result = api_no_db.post(
        "/api/v1/instruments",
        json={"secret_field": "DO_NOT_ECHO"},
        headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN},
    )
    assert result.status_code == 422 and "DO_NOT_ECHO" not in result.text
    assert "traceback" not in result.text.lower()
