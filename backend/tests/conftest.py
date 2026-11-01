"""Synthetic fixtures only. Integration cleanup is restricted to a disposable *_test database."""

import os
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from app.config import Settings
from app.main import create_app

TOKEN = "synthetic-test-token-not-a-real-secret-000000"
ORIGIN = "http://127.0.0.1:5173"
ROOT = Path(__file__).resolve().parents[2]


def test_settings(url="postgresql+psycopg://test:test@127.0.0.1:1/bullion_test", **kwargs):
    return Settings(
        _env_file=None,
        database_url=url,
        local_app_token=TOKEN,
        allowed_hosts="127.0.0.1,localhost,testserver",
        **kwargs,
    )


@pytest.fixture
def api_no_db(monkeypatch):
    monkeypatch.setattr("app.main.schema_ready", lambda engine: False)
    app = create_app(test_settings(max_import_bytes=1024))
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def db_engine():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip(
            "TEST_DATABASE_URL not set: disposable PostgreSQL integration tests not executed"
        )
    parsed = make_url(url)
    if (
        parsed.drivername != "postgresql+psycopg"
        or parsed.host not in {"127.0.0.1", "localhost", "test-db"}
        or not (parsed.database or "").endswith("_test")
    ):
        pytest.fail(
            "Refusing integration cleanup outside a local disposable *_test PostgreSQL database"
        )
    os.environ["DATABASE_URL"] = url
    os.environ["LOCAL_APP_TOKEN"] = TOKEN
    config = Config(str(ROOT / "backend/alembic.ini"))
    command.upgrade(config, "head")
    engine = create_engine(url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture
def api(db_engine):
    # This database is explicitly disposable; never target the application volume.
    with db_engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE quality_results, price_observations, import_rows, import_batches, watchlist_members, watchlists, data_sources, instruments"
            )
        )
    app = create_app(test_settings(db_engine.url.render_as_string(hide_password=False)))
    with TestClient(app, headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}) as client:
        yield client
