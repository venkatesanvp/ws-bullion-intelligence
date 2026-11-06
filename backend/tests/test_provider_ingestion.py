"""PostgreSQL provider persistence and existing research integration. Synthetic data only."""

from dataclasses import replace
from decimal import Decimal
import json
from uuid import uuid4

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.acquisition import preflight
from app.dhan_import import main
from app.errors import APIError
from app.models import DataSource, ImportBatch, ImportRow, Instrument, Observation
from app.provider_ingestion import ingest_collected
from .provider_fixtures import TOKEN, collected, metadata, plan, provider_for, register


def import_first(db, result, source_id, instrument_ids, *, key=None, approved=True):
    series = result.series[0]
    return ingest_collected(
        db,
        series,
        metadata(series, source_id, instrument_ids[0]),
        key or uuid4(),
        "synthetic-run",
        persistence_approved=approved,
    )


def test_four_primary_one_year_import_research_charts_indicators_and_comparisons(api, db_engine):
    p, result, _ = collected()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        for i, item in enumerate(result.series):
            status, payload = ingest_collected(
                db,
                item,
                metadata(item, source, ids[i]),
                uuid4(),
                "synthetic",
                persistence_approved=True,
            )
            assert status == 201 and payload["data"]["new_count"] == 261
        assert db.scalar(select(func.count()).select_from(Observation)) == 4 * 261
        first = db.scalar(
            select(Observation)
            .where(Observation.instrument_id == ids[0])
            .order_by(Observation.trading_date)
        )
        assert first.close == Decimal("101") and first.event_time is None
        batch = db.get(ImportBatch, first.batch_id)
        assert (
            batch.profile_snapshot["acquisition"]["chunks"][0]["provenance"]["provider"] == "DHANHQ"
        )
        assert batch.profile_snapshot["source_profile"]["data_class"] == "SYNTHETIC_TEST"
        raw = db.get(ImportRow, (first.batch_id, first.row_number)).mapped_raw
        assert "source_timestamp" in raw and "retrieved_at" in raw and TOKEN not in json.dumps(raw)
    parameters = {
        "source_id": str(source),
        "basis": "PROVIDER_ADJUSTED",
        "start": str(p.start),
        "end": str(p.end),
    }
    chart = api.get(f"/api/v1/instruments/{ids[0]}/chart", params=parameters)
    assert chart.status_code == 200 and len(chart.json()["data"]["points"]) == 261
    assert chart.json()["meta"]["source"]["source_kind"] == "DHANHQ"
    assert "TIMESTAMP_CONTRACT_UNVERIFIED" in chart.json()["meta"]["quality"]["flags"]
    for name, n in [("SMA", 20), ("SMA", 50), ("SMA", 200), ("EMA", 37), ("RSI", 14)]:
        response = api.get(
            f"/api/v1/instruments/{ids[0]}/indicators",
            params={**parameters, "indicator": name, "n": n},
        )
        assert response.status_code == 200
        values = response.json()["data"]["values"]
        assert values[-1]["value"] is not None
        if name == "SMA":
            assert Decimal(values[-1]["value"]) == Decimal(361) - Decimal(n - 1) / 2
    for a, b in [(0, 2), (1, 3)]:
        comparison = api.post(
            "/api/v1/comparisons",
            json={
                "series": [
                    {
                        "instrument_id": str(ids[i]),
                        "source_id": str(source),
                        "price_basis": "PROVIDER_ADJUSTED",
                    }
                    for i in (a, b)
                ],
                "start": str(p.start),
                "end": str(p.end),
            },
        )
        assert comparison.status_code == 200, comparison.text
        assert comparison.json()["data"]["common_observation_count"] == 261
        assert "PRICE_ONLY_NOT_TOTAL_RETURN" in comparison.json()["data"]["limitations"]


def test_same_key_replay_and_new_key_duplicates_preserve_original_provenance(api, db_engine):
    p, result, _ = collected()
    key = uuid4()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        _, first = import_first(db, result, source, ids, key=key)
        _, second = import_first(db, result, source, ids, key=key)
        assert second["data"]["replayed"] and second["data"]["id"] == first["data"]["id"]
        _, repeat = import_first(db, result, source, ids)
        assert repeat["data"]["status"] == "NO_CHANGE" and repeat["data"]["duplicate_count"] == 261
        assert db.scalar(select(func.count()).select_from(Observation)) == 261
        instrument = db.get(Instrument, ids[0])
        assert instrument.data_revision == 1


def test_conflicting_observation_rejects_entire_import(api, db_engine):
    p, result, _ = collected()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        import_first(db, result, source, ids)
        series = result.series[0]
        chunk = series.chunks[0]
        row = replace(chunk.observations[0], close=Decimal("102"))
        bad = replace(
            series, chunks=(replace(chunk, observations=(row,) + chunk.observations[1:]),)
        )
        status, payload = ingest_collected(
            db, bad, metadata(bad, source, ids[0]), uuid4(), "synthetic", persistence_approved=True
        )
        assert status == 409 and payload["data"]["status"] == "REJECTED"
        assert payload["data"]["new_count"] == 0
        assert db.scalar(select(func.count()).select_from(Observation)) == 261


def test_missing_sessions_recorded_and_indicator_segments_break(api, db_engine):
    p = plan()
    absent = p.calendar.session_dates[-8]
    _, result, _ = collected(p, missing=(absent,))
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        _, payload = import_first(db, result, source, ids)
        assert payload["data"]["new_count"] == 260
    response = api.get(
        f"/api/v1/instruments/{ids[0]}/indicators",
        params={
            "source_id": str(source),
            "basis": "PROVIDER_ADJUSTED",
            "indicator": "SMA",
            "n": 20,
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["values"][-1]["value"] is None
    assert response.json()["meta"]["quality"]["missing_session_count"] == 1


@pytest.mark.parametrize("kind", ["rights", "policy", "approval", "identity"])
def test_persistence_guards_before_price_writes(api, db_engine, kind):
    p, result, _ = collected()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p, rights=kind != "rights")
        if kind == "policy":
            with db.begin():
                db.get(DataSource, source).profile = {
                    **db.get(DataSource, source).profile,
                    "acquisition_review": None,
                }
        if kind == "identity":
            with db.begin():
                db.get(Instrument, ids[0]).isin = "INF000000000"
        with pytest.raises(APIError):
            import_first(db, result, source, ids, approved=kind != "approval")
        assert db.scalar(select(func.count()).select_from(Observation)) == 0


def test_invalid_canonical_observation_not_retained_as_raw_payload(api, db_engine):
    p, result, _ = collected()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        series = result.series[0]
        chunk = series.chunks[0]
        row = replace(chunk.observations[0], volume=-1)
        bad = replace(
            series, chunks=(replace(chunk, observations=(row,) + chunk.observations[1:]),)
        )
        status, payload = ingest_collected(
            db, bad, metadata(bad, source, ids[0]), uuid4(), "synthetic", persistence_approved=True
        )
        assert status == 422 and payload["data"]["status"] == "REJECTED"
        assert db.scalar(select(func.count()).select_from(Observation)) == 0
        assert db.scalar(select(func.count()).select_from(ImportRow)) == 260


def test_interruption_rolls_back_batch_rows_revision_and_retries_safely(api, db_engine):
    p, result, _ = collected()
    key = uuid4()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)

        def fail_after_flush(session, context):
            if any(isinstance(x, Observation) for x in session.new):
                raise SQLAlchemyError("synthetic interruption")

        event.listen(db, "after_flush", fail_after_flush)
        try:
            with pytest.raises(SQLAlchemyError):
                import_first(db, result, source, ids, key=key)
        finally:
            event.remove(db, "after_flush", fail_after_flush)
        assert db.scalar(select(func.count()).select_from(ImportBatch)) == 0
        assert db.scalar(select(func.count()).select_from(Observation)) == 0
        assert db.get(Instrument, ids[0]).data_revision == 0
        db.rollback()
        _, payload = import_first(db, result, source, ids, key=key)
        assert payload["data"]["new_count"] == 261


def test_import_committed_before_lost_ack_replays_without_duplication(api, db_engine):
    p, result, _ = collected()
    key = uuid4()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        import_first(
            db, result, source, ids, key=key
        )  # Simulated lost acknowledgement after commit.
    with Session(db_engine) as db:
        _, payload = import_first(db, result, source, ids, key=key)
        assert payload["data"]["replayed"]
        assert db.scalar(select(func.count()).select_from(Observation)) == 261


def test_source_kind_contract_api_and_csv_mismatch(api):
    profile = {"data_class": "SYNTHETIC_TEST", "policy_version": "quality-v1"}
    assert (
        api.post(
            "/api/v1/data-sources",
            json={"label": "SYNTHETIC mismatch", "source_kind": "DHANHQ", "profile": profile},
        ).status_code
        == 422
    )
    source = api.post(
        "/api/v1/data-sources",
        json={
            "label": "SYNTHETIC provider",
            "source_kind": "DHANHQ",
            "contract_version": "dhan-daily-v1-provisional",
            "profile": profile,
        },
    )
    assert source.status_code == 201 and source.json()["data"]["source_kind"] == "DHANHQ"


def test_manual_cli_persistence_and_stable_run_recovery(api, db_engine, tmp_path, capsys):
    p, result, _ = collected()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
    provider, calls = provider_for(p)
    path = tmp_path / "plan.json"
    path.write_text(p.model_dump_json())
    run = uuid4()
    args = [
        "--plan",
        str(path),
        "--env-file",
        str(tmp_path / "no-env"),
        "--execute-approved-plan",
        preflight(provider, p)["plan_fingerprint"],
        "--persist-approved",
        "--source-id",
        str(source),
        "--run-id",
        str(run),
    ]
    for repeat in (False, True):
        assert (
            main(
                args,
                provider_factory=lambda _: provider,
                session_factory=lambda: Session(db_engine),
                pause=lambda _: None,
            )
            == 0
        )
        output = json.loads(capsys.readouterr().out)
        assert len(output["imports"]) == 4 and all(
            x["replayed"] == repeat for x in output["imports"]
        )
        assert TOKEN not in json.dumps(output)
    assert len(calls) == 8  # Two explicitly authorized mocked runs, never automatic retries.
    with Session(db_engine) as db:
        assert db.scalar(select(func.count()).select_from(Observation)) == 1044


def test_unqualified_cli_source_blocks_before_provider(api, db_engine, tmp_path, capsys):
    p, result, _ = collected()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p, rights=False)
    provider, calls = provider_for(p)
    path = tmp_path / "plan.json"
    path.write_text(p.model_dump_json())
    args = [
        "--plan",
        str(path),
        "--env-file",
        str(tmp_path / "no-env"),
        "--execute-approved-plan",
        preflight(provider, p)["plan_fingerprint"],
        "--persist-approved",
        "--source-id",
        str(source),
        "--run-id",
        str(uuid4()),
    ]
    assert (
        main(
            args,
            provider_factory=lambda _: provider,
            session_factory=lambda: Session(db_engine),
            pause=lambda _: None,
        )
        == 1
    )
    assert not calls and json.loads(capsys.readouterr().out)["code"] == "SOURCE_NOT_QUALIFIED"


def test_concurrent_same_request_is_one_atomic_import(api, db_engine):
    from concurrent.futures import ThreadPoolExecutor

    p, result, _ = collected()
    key = uuid4()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)

    def attempt():
        with Session(db_engine) as db:
            return import_first(db, result, source, ids, key=key)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: attempt(), range(2)))
    assert sorted(status for status, _ in results) == [200, 201]
    with Session(db_engine) as db:
        assert db.scalar(select(func.count()).select_from(Observation)) == 261
        assert db.scalar(select(func.count()).select_from(ImportBatch)) == 1


def test_migration_preserves_csv_and_refuses_destructive_provider_downgrade(api, db_engine):
    from pathlib import Path
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import text
    from .test_integration import seed, upload

    instrument, source, meta = seed(api)
    assert upload(api, meta).status_code == 201
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with db_engine.connect() as connection:
        original = connection.scalar(select(func.count()).select_from(Observation))
    try:
        command.downgrade(config, "0001_market_workbench")
        command.upgrade(config, "head")
        with db_engine.connect() as connection:
            assert connection.scalar(select(func.count()).select_from(Observation)) == original
    finally:
        command.upgrade(config, "head")
    p, result, _ = collected()
    # Use a separate provider source; original CSV listing has a different synthetic symbol.
    with Session(db_engine) as db:
        register(db, result.series, p)
    with pytest.raises(Exception):
        command.downgrade(config, "0001_market_workbench")
    with db_engine.connect() as connection:
        assert (
            connection.scalar(text("SELECT version_num FROM alembic_version"))
            == "0002_provider_ingestion"
        )
        assert connection.scalar(select(func.count()).select_from(Observation)) == original


def test_changed_calendar_is_rejected_before_persistence(api, db_engine):
    p, result, _ = collected()
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        with db.begin():
            item = db.get(DataSource, source)
            changed = dict(item.profile["calendar"])
            changed["session_dates"] = changed["session_dates"][:-1]
            item.profile = {**item.profile, "calendar": changed}
        with pytest.raises(APIError) as caught:
            import_first(db, result, source, ids)
        assert caught.value.code == "SOURCE_CALENDAR_CHANGED"
        assert db.scalar(select(func.count()).select_from(Observation)) == 0


def test_missing_final_requested_session_remains_visible_in_research(api, db_engine):
    p = plan()
    absent = p.calendar.session_dates[-1]
    _, result, _ = collected(p, missing=(absent,))
    with Session(db_engine) as db:
        source, ids = register(db, result.series, p)
        import_first(db, result, source, ids)
    response = api.get(
        f"/api/v1/instruments/{ids[0]}/chart",
        params={
            "source_id": str(source),
            "basis": "PROVIDER_ADJUSTED",
            "start": str(p.start),
            "end": str(p.end),
        },
    )
    assert response.status_code == 200
    assert response.json()["meta"]["quality"]["missing_session_dates"] == [str(absent)]
    assert response.json()["meta"]["quality"]["continuity"] == "ASSESSED_WITH_GAPS"
    assert response.json()["data"]["points"][-1]["trading_date"] != str(absent)
