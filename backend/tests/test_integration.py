"""Real PostgreSQL acceptance for DC-01..04/07/09; all market values are SYNTHETIC_TEST."""

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import UUID, uuid4
import json
import pytest
from sqlalchemy import event, func, inspect, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.ingestion import ingest
from app.models import ImportBatch, ImportRow, Instrument, Observation
from app.schemas import ImportMetadata
from .conftest import test_settings as settings_for_test

CSV = "trading_date,close\n2026-01-01,10.1234567890\n2026-01-02,12\n"


def create(client, path, data):
    result = client.post("/api/v1/" + path, json=data)
    assert result.status_code == 201, result.text
    return result.json()["data"]


def seed(client, *, qualified=True, profile=None, symbol="SYNTH_GOLD"):
    instrument = create(
        client,
        "instruments",
        {
            "exchange": "XNSE",
            "symbol": symbol,
            "name": "SYNTHETIC TEST listing; not a real ETF",
            "metal": "GOLD",
            "currency": "INR",
        },
    )
    source = create(
        client,
        "data-sources",
        {
            "label": "SYNTHETIC TEST generated fixture",
            "profile": {
                "data_class": "SYNTHETIC_TEST",
                "policy_version": "quality-v1",
                **(profile or {}),
            },
        },
    )
    if qualified:
        result = client.patch(
            "/api/v1/data-sources/" + source["id"] + "/qualification",
            json={
                "qualification": "QUALIFIED_FOR_RESEARCH",
                "rights_evidence_ref": "TEST ONLY: generated fixture",
                "retention_review_ref": "TEST ONLY: disposable database",
                "permitted_uses": dict.fromkeys(
                    ["retrieval", "storage", "analysis", "display"], True
                ),
            },
        )
        assert result.status_code == 200, result.text
        source = result.json()["data"]
    metadata = {
        "instrument_id": instrument["id"],
        "source_id": source["id"],
        "interval": "1d",
        "price_basis": "RAW_CLOSE",
        "mapping_version": "test-v1",
        "column_map": {"trading_date": "trading_date", "close": "close"},
        "quality_policy_version": "quality-v1",
        "qualification_ref": "TEST ONLY: generated fixture",
    }
    return instrument, source, metadata


def upload(client, metadata, value=CSV, key=None, filename="synthetic-test.csv"):
    return client.post(
        "/api/v1/import-batches",
        files={"file": (filename, value, "text/csv")},
        data={"metadata_json": json.dumps(metadata)},
        headers={"Idempotency-Key": str(key or uuid4())},
    )


def history(client, metadata, **params):
    return client.get(
        "/api/v1/instruments/" + metadata["instrument_id"] + "/history",
        params={"source_id": metadata["source_id"], "basis": metadata["price_basis"], **params},
    )


def test_migration_revision_and_constraints(api, db_engine):
    assert (
        api.get("/api/v1/health/ready").json()["data"]["schema_revision"] == "0002_provider_ingestion"
    )
    expected = {
        "instruments",
        "data_sources",
        "import_batches",
        "import_rows",
        "price_observations",
        "quality_results",
        "watchlists",
        "watchlist_members",
        "alembic_version",
    }
    assert expected == set(inspect(db_engine).get_table_names())
    assert {"uq_observation", "uq_observation_raw_row"} <= {
        c["name"] for c in inspect(db_engine).get_unique_constraints("price_observations")
    }


def test_listing_and_watchlist_persistence(api):
    instrument, _, meta = seed(api)
    assert upload(api, meta).status_code == 201
    watchlist = create(api, "watchlists", {"name": "Synthetic research"})
    member_path = "/api/v1/watchlists/" + watchlist["id"] + "/members"
    assert api.post(member_path, json={"instrument_id": instrument["id"]}).status_code == 201
    assert api.post(member_path, json={"instrument_id": instrument["id"]}).status_code == 200
    assert (
        api.patch(
            "/api/v1/watchlists/" + watchlist["id"], json={"name": "Renamed test"}
        ).status_code
        == 200
    )
    assert len(api.get("/api/v1/watchlists/" + watchlist["id"]).json()["data"]["members"]) == 1
    assert api.delete(member_path + "/" + instrument["id"]).status_code == 204
    assert api.delete(member_path + "/" + instrument["id"]).status_code == 204
    assert history(api, meta).json()["meta"]["coverage"]["count"] == 2
    assert (
        api.patch(
            "/api/v1/instruments/" + instrument["id"], json={"name": "New display", "active": False}
        ).status_code
        == 200
    )
    assert api.patch(
        "/api/v1/instruments/" + instrument["id"], json={"symbol": "OTHER"}
    ).status_code in {409, 422}
    duplicate = api.post(
        "/api/v1/instruments",
        json={
            "exchange": "XNSE",
            "symbol": "SYNTH_GOLD",
            "name": "duplicate",
            "metal": "GOLD",
            "currency": "INR",
        },
    )
    assert duplicate.status_code == 409


def test_source_gate_and_restriction(api):
    _, source, meta = seed(api, qualified=False)
    assert upload(api, meta).status_code == 403
    assert history(api, meta).status_code == 403
    invalid = api.patch(
        "/api/v1/data-sources/" + source["id"] + "/qualification",
        json={
            "qualification": "QUALIFIED_FOR_RESEARCH",
            "permitted_uses": dict.fromkeys(["retrieval", "storage", "analysis", "display"], True),
        },
    )
    assert invalid.status_code == 422


def test_decimal_and_raw_temporal_provenance(api, db_engine):
    _, _, meta = seed(api)
    result = upload(api, meta)
    assert result.status_code == 201, result.text
    batch = result.json()["data"]
    data = history(api, meta).json()
    first = data["data"][0]
    assert first["close"] == "10.1234567890"
    assert first["provider_published_at"] is None and first["event_time"] is None
    assert first["event_precision"] == "SESSION_DATE"
    assert first["batch_id"] == batch["id"] and first["row_number"] == 1
    assert data["meta"]["source"]["data_class"] == "SYNTHETIC_TEST"
    assert data["meta"]["freshness"]["status"] == "UNASSESSED"
    assert "UNVERIFIED_FOR_REPLAY" in data["meta"]["limitations"]
    with Session(db_engine) as db:
        raw = db.get(ImportRow, (UUID(batch["id"]), 1))
        assert raw.mapped_raw == {"trading_date": "2026-01-01", "close": "10.1234567890"}


def test_idempotence_new_key_duplicates_and_conflicts(api):
    _, _, meta = seed(api)
    key = uuid4()
    original = upload(api, meta, key=key)
    assert original.status_code == 201
    batch_id = original.json()["data"]["id"]
    replay = upload(api, meta, key=key)
    assert replay.status_code == 200 and replay.json()["data"]["id"] == batch_id
    assert replay.json()["data"]["replayed"]
    assert upload(api, meta, CSV.replace(",12", ",13"), key).status_code == 409
    assert upload(api, {**meta, "mapping_version": "changed"}, key=key).status_code == 409
    duplicate = upload(
        api, meta, "trading_date,close\n2026-01-02,12.00\n2026-01-01,10.1234567890\n"
    )
    assert duplicate.status_code == 201 and duplicate.json()["data"]["status"] == "NO_CHANGE"
    assert duplicate.json()["data"]["duplicate_count"] == 2
    conflict = upload(api, meta, "trading_date,close\n2026-01-01,99\n2026-01-03,15\n")
    assert conflict.status_code == 409 and conflict.json()["data"]["new_count"] == 0
    assert history(api, meta).json()["meta"]["coverage"]["count"] == 2
    assert history(api, meta).json()["meta"]["series_ref"]["revision"] == 1
    resolved = api.get("/api/v1/import-batches/by-key/" + str(key))
    assert resolved.json()["data"]["id"] == batch_id
    assert api.get("/api/v1/import-batches/by-key/" + str(uuid4())).status_code == 404


@pytest.mark.parametrize(
    "value",
    [
        "trading_date,close\n2026-01-01,10\n2026-01-02,NaN\n",
        "trading_date,close\n2026-01-01,10\n2026-01-01,11\n",
        "trading_date,close,PRIVATE_ACCOUNT\n2026-01-01,10,SECRET\n",
        "trading_date,close\n",
    ],
)
def test_atomic_rejections_and_safe_issues(api, db_engine, value):
    _, _, meta = seed(api)
    result = upload(api, meta, value)
    assert result.status_code in {409, 422}
    batch = result.json()["data"]
    assert batch["status"] == "REJECTED" and batch["new_count"] == 0
    with Session(db_engine) as db:
        assert db.scalar(select(func.count()).select_from(Observation)) == 0
        assert db.scalar(select(func.count()).select_from(ImportBatch)) == 1
        if "PRIVATE_ACCOUNT" in value:
            assert db.scalar(select(func.count()).select_from(ImportRow)) == 0
    issues = api.get("/api/v1/import-batches/" + batch["id"] + "/issues")
    assert issues.status_code == 200 and issues.json()["data"]
    assert "SECRET" not in issues.text


def test_history_cursor_revision_and_profile(api):
    _, source, meta = seed(api)
    assert upload(api, meta).status_code == 201
    first = history(api, meta, limit=1).json()
    cursor = first["meta"]["page"]["next_cursor"]
    second = history(api, meta, limit=1, cursor=cursor)
    assert second.status_code == 200 and second.json()["data"][0]["trading_date"] == "2026-01-02"
    assert history(api, meta, limit=1, cursor=cursor, start="2026-01-02").status_code == 409
    assert upload(api, meta, "trading_date,close\n2026-01-03,15\n").status_code == 201
    assert history(api, meta, cursor=cursor).json()["error"]["code"] == "SNAPSHOT_CHANGED"
    new_cursor = history(api, meta, limit=1).json()["meta"]["page"]["next_cursor"]
    change = {
        "qualification": "QUALIFIED_FOR_RESEARCH",
        "rights_evidence_ref": "TEST ONLY: generated fixture",
        "retention_review_ref": "TEST ONLY",
        "permitted_uses": dict.fromkeys(["retrieval", "storage", "analysis", "display"], True),
        "profile": {**source["profile"], "known_break_dates": ["2026-01-02"]},
    }
    assert (
        api.patch(
            "/api/v1/data-sources/" + source["id"] + "/qualification", json=change
        ).status_code
        == 200
    )
    assert history(api, meta, cursor=new_cursor).status_code == 409
    assert api.get("/api/v1/instruments/" + meta["instrument_id"] + "/history").status_code == 422
    assert history(api, meta, start="2026-02-01", end="2026-01-01").status_code == 422


def test_calendar_freshness_window_separation(api):
    profile = {
        "calendar": {
            "evidence_ref": "SYNTHETIC",
            "version": "test-1",
            "coverage_start": "2026-01-01",
            "coverage_end": "2026-01-03",
            "session_dates": ["2026-01-01", "2026-01-02", "2026-01-03"],
        },
        "freshness": {
            "evidence_ref": "SYNTHETIC",
            "assessment_as_of": "2026-01-03T18:00:00Z",
            "expected_latest_session": "2026-01-03",
        },
    }
    _, _, meta = seed(api, profile=profile)
    assert (
        upload(api, meta, "trading_date,close\n2026-01-01,10\n2026-01-03,12\n").status_code == 201
    )
    result = history(
        api, meta, start="2026-01-01", end="2026-01-01", assessment_as_of="2026-01-03T18:00:00Z"
    ).json()["meta"]
    assert result["coverage"]["range_last_date"] == "2026-01-01"
    assert result["coverage"]["dataset_last_date"] == "2026-01-03"
    assert result["freshness"]["status"] == "FRESH"
    full = history(api, meta).json()["meta"]
    assert full["quality"]["missing_session_dates"] == ["2026-01-02"]
    assert full["freshness"]["status"] == "UNASSESSED"
    assert history(api, meta, assessment_as_of="2026-01-03T18:00:00").status_code == 422
    outside = history(api, meta, start="2025-12-01").json()["meta"]
    assert outside["quality"]["continuity"] == "PARTIALLY_ASSESSED"


def test_request_limits_and_explicit_mapping(api):
    _, _, meta = seed(api)
    assert upload(api, meta, filename="../escape.csv").status_code == 415
    assert upload(api, meta, filename="file.zip").status_code == 415
    assert upload(api, {**meta, "interval": "1h"}).status_code == 422
    assert (
        upload(
            api, {**meta, "column_map": {"trading_date": "eval()", "close": "close"}}
        ).status_code
        == 422
    )
    assert upload(api, {**meta, "price_basis": "PROVIDER_ADJUSTED"}).status_code == 422
    assert api.get("/api/v1/instruments?limit=1001").status_code == 422


@pytest.mark.parametrize("same_key", [True, False])
def test_concurrent_duplicate_imports(api, db_engine, same_key):
    _, _, meta = seed(api)
    shared = uuid4()

    def send(_):
        # Separate sessions/connections; the same-key advisory lock and listing lock serialize writes.
        with Session(db_engine) as db:
            return ingest(
                db,
                CSV.encode(),
                "synthetic-test.csv",
                ImportMetadata(**meta),
                shared if same_key else uuid4(),
                str(uuid4()),
                100,
            )[0]

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(send, range(2)))
    assert sorted(results) == ([200, 201] if same_key else [201, 201])
    with Session(db_engine) as db:
        assert db.scalar(select(func.count()).select_from(Observation)) == 2
        assert db.scalar(select(Instrument.data_revision)) == 1
        assert db.scalar(select(func.count()).select_from(ImportBatch)) == (1 if same_key else 2)


def test_failure_before_commit_and_lost_response_recovery(api, db_engine):
    _, _, meta = seed(api)
    key = uuid4()
    with Session(db_engine) as db:

        def fail_commit(session):
            raise SQLAlchemyError("SYNTHETIC injected commit failure")

        event.listen(db, "before_commit", fail_commit, once=True)
        with pytest.raises(SQLAlchemyError):
            ingest(
                db,
                CSV.encode(),
                "synthetic-test.csv",
                ImportMetadata(**meta),
                key,
                str(uuid4()),
                100,
            )
    with Session(db_engine) as db:
        assert db.scalar(select(func.count()).select_from(Observation)) == 0
        assert db.scalar(select(func.count()).select_from(ImportBatch)) == 0
    # Simulate a committed response being lost: deliberately discard it, then resolve/retry its key.
    assert upload(api, meta, key=key).status_code == 201
    resolved = api.get("/api/v1/import-batches/by-key/" + str(key)).json()["data"]
    retried = upload(api, meta, key=key)
    assert retried.status_code == 200 and retried.json()["data"]["id"] == resolved["id"]


def test_persistence_across_app_restart(api, db_engine):
    from fastapi.testclient import TestClient
    from app.main import create_app
    from .conftest import TOKEN, ORIGIN

    _, _, meta = seed(api)
    assert upload(api, meta).status_code == 201
    create(api, "watchlists", {"name": "Restart evidence"})
    other_app = create_app(settings_for_test(db_engine.url.render_as_string(hide_password=False)))
    with TestClient(
        other_app, headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}
    ) as restarted:
        assert history(restarted, meta).json()["meta"]["coverage"]["count"] == 2
        assert restarted.get("/api/v1/watchlists").json()["data"][0]["name"] == "Restart evidence"


def test_database_constraints_and_immutable_observation(api, db_engine):
    _, _, meta = seed(api)
    assert upload(api, meta).status_code == 201
    with db_engine.begin() as conn:
        original = conn.execute(
            text("SELECT close FROM price_observations ORDER BY trading_date LIMIT 1")
        ).scalar_one()
    assert original == Decimal("10.1234567890")
    # Accepted financial history is append-only even for accidental direct SQL writes.
    with pytest.raises(SQLAlchemyError):
        with db_engine.begin() as conn:
            conn.execute(text("UPDATE price_observations SET close = 99"))
    with pytest.raises(IntegrityError):
        with db_engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO watchlist_members (watchlist_id, instrument_id, added_at) VALUES (:w,:i,now())"
                ),
                {"w": uuid4(), "i": uuid4()},
            )
    assert history(api, meta).json()["data"][0]["close"] == "10.1234567890"


def test_concurrent_conflicts_and_global_request_key(api, db_engine):
    from app.errors import APIError

    _, _, first = seed(api)
    _, _, second = seed(api, symbol="SYNTH_SILVER_GLOBAL")
    shared = uuid4()

    def send(meta):
        with Session(db_engine) as db:
            try:
                return ingest(
                    db,
                    CSV.encode(),
                    "synthetic.csv",
                    ImportMetadata(**meta),
                    shared,
                    str(uuid4()),
                    100,
                )[0]
            except APIError as exc:
                return exc.status

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(send, [first, second]))
    assert sorted(results) == [201, 409]
    with Session(db_engine) as db:
        assert db.scalar(select(func.count()).select_from(ImportBatch)) == 1
        assert db.scalar(select(func.count()).select_from(Observation)) == 2


def test_source_policy_lock_prevents_import_after_restriction(api, db_engine):
    from threading import Event
    from app.errors import APIError
    from app.models import DataSource

    _, source, meta = seed(api)
    started = Event()

    def send():
        with Session(db_engine) as db:
            started.set()
            try:
                return ingest(
                    db,
                    CSV.encode(),
                    "synthetic.csv",
                    ImportMetadata(**meta),
                    uuid4(),
                    str(uuid4()),
                    100,
                )[0]
            except APIError as exc:
                return exc.status

    with Session(db_engine) as owner, ThreadPoolExecutor(max_workers=1) as executor:
        with owner.begin():
            locked = owner.scalar(
                select(DataSource).where(DataSource.id == UUID(source["id"])).with_for_update()
            )
            locked.qualification = "RESTRICTED"
            future = executor.submit(send)
            assert started.wait(5)
        assert future.result(timeout=10) == 403
    with Session(db_engine) as db:
        assert db.scalar(select(func.count()).select_from(Observation)) == 0


def test_identity_correction_before_history_and_synthetic_relabel_block(api):
    listing, source, meta = seed(api)
    path = "/api/v1/instruments/" + listing["id"]
    assert api.patch(path, json={"name": "Corrected display", "isin": None}).status_code == 200
    assert api.patch(path, json={"symbol": "SYNTH_CORRECTED"}).status_code == 200
    assert upload(api, meta).status_code == 201
    assert (
        api.patch(path, json={"symbol": "SYNTH_CHANGED"}).json()["error"]["code"]
        == "IMMUTABLE_IDENTITY"
    )
    review = {
        "qualification": "QUALIFIED_FOR_RESEARCH",
        "rights_evidence_ref": "TEST ONLY",
        "retention_review_ref": "TEST ONLY",
        "permitted_uses": dict.fromkeys(["retrieval", "storage", "analysis", "display"], True),
        "profile": {**source["profile"], "data_class": "REAL_MARKET"},
    }
    assert (
        api.patch(
            "/api/v1/data-sources/" + source["id"] + "/qualification", json=review
        ).status_code
        == 409
    )
    assert history(api, meta).json()["meta"]["source"]["data_class"] == "SYNTHETIC_TEST"


@pytest.mark.parametrize("start,end", [("2025-12-31", "2026-01-04"), ("2026-01-01", "2026-01-03")])
def test_calendar_gaps_only_between_observed_endpoints(api, start, end):
    """VS01-T-10/17: range extension cannot invent pre/post-history missing bars."""
    profile = {
        "calendar": {
            "evidence_ref": "SYNTHETIC TEST ONLY",
            "version": "test-bounds",
            "coverage_start": "2025-12-31",
            "coverage_end": "2026-01-04",
            "session_dates": ["2025-12-31", "2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        }
    }
    _, _, metadata = seed(api, profile=profile)
    assert (
        upload(api, metadata, "trading_date,close\n2026-01-01,10\n2026-01-03,12\n").status_code
        == 201
    )
    result = history(api, metadata, start=start, end=end).json()["meta"]
    assert result["quality"]["missing_session_dates"] == ["2026-01-02"]
    assert result["quality"]["missing_session_count"] == 1
    assert result["coverage"]["range_first_date"] == "2026-01-01"
    assert result["coverage"]["range_last_date"] == "2026-01-03"


def test_explicit_freshness_stale_empty_and_nonmatching_as_of(api):
    """VS01-T-10: only the reviewed as-of context can assess freshness."""
    profile = {
        "freshness": {
            "evidence_ref": "SYNTHETIC TEST ONLY",
            "assessment_as_of": "2026-01-03T18:00:00Z",
            "expected_latest_session": "2026-01-03",
        }
    }
    _, _, metadata = seed(api, profile=profile)
    empty = history(api, metadata, assessment_as_of="2026-01-03T18:00:00Z").json()["meta"]
    assert empty["freshness"]["status"] == "UNASSESSED"
    assert empty["freshness"]["actual_latest_date"] is None
    assert upload(api, metadata).status_code == 201
    stale = history(api, metadata, assessment_as_of="2026-01-03T18:00:00Z").json()["meta"]
    assert stale["freshness"]["status"] == "STALE"
    assert stale["freshness"]["actual_latest_date"] == "2026-01-02"
    assert (
        history(api, metadata, assessment_as_of="2026-01-04T18:00:00Z").json()["meta"]["freshness"][
            "status"
        ]
        == "UNASSESSED"
    )


def test_wrong_migration_revision_blocks_readiness_and_data(api, db_engine):
    """VS01-T-21: a reachable database with the wrong schema cannot serve data."""
    with db_engine.begin() as connection:
        connection.execute(
            text("UPDATE alembic_version SET version_num='synthetic_wrong_revision'")
        )
    try:
        assert api.get("/api/v1/health/live").status_code == 200
        assert api.get("/api/v1/health/ready").status_code == 503
        response = api.get("/api/v1/instruments")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "DEPENDENCY_NOT_READY"
    finally:
        with db_engine.begin() as connection:
            connection.execute(
                text("UPDATE alembic_version SET version_num='0002_provider_ingestion'")
            )
