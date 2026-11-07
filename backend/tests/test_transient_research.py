"""Offline tests for transient real-data delivery; HTTP responses/prices are synthetic."""

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.acquisition import HistoryPlan
from app.main import create_app
from app.models import Observation, ImportBatch, ImportRow, DataSource
from app.transient_research import TransientResearch
from app.transient_uat import APPROVED_FINGERPRINT, NAMES
from .conftest import test_settings as settings_for_transient, TOKEN, ORIGIN
from .provider_fixtures import provider_for, collected


def test_shared_canonical_transient_install_and_restart_lifetime():
    p, result, _ = collected()
    memory = TransientResearch()
    memory.install(result, p, names=NAMES, data_class="SYNTHETIC_TEST")
    listing = memory.listings()[0]
    source = memory.sources()[0]
    assert source.qualification == "TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED"
    assert source.permitted_uses["storage"] is False
    assert len(memory.points(listing.id, source.id, "PROVIDER_ADJUSTED")) == 261
    assert (
        memory.meta(listing, source, "PROVIDER_ADJUSTED", p.start, p.end)["quality"][
            "missing_session_count"
        ]
        == 0
    )
    assert TransientResearch().report()["status"] == "NOT_LOADED"


def test_memory_install_rejects_bad_canonical_row_atomically():
    p, result, _ = collected()
    first = result.series[0]
    chunk = first.chunks[0]
    bad = replace(chunk.observations[0], volume=-1)
    result = replace(
        result,
        series=(
            replace(first, chunks=(replace(chunk, observations=(bad,) + chunk.observations[1:]),)),
        )
        + result.series[1:],
    )
    memory = TransientResearch()
    with pytest.raises(Exception):
        memory.install(result, p, names=NAMES)
    assert not memory.listings()


def test_one_process_live_claim_is_atomic():
    memory = TransientResearch()

    def attempt(_):
        try:
            memory.claim()
            return "claimed"
        except Exception:
            return "blocked"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sorted(results) == ["blocked", "claimed"]


def test_authenticated_one_shot_loader_drives_existing_research_without_price_writes(
    api, db_engine
):
    p = HistoryPlan.model_validate_json(
        (
            Path(__file__).resolve().parents[2] / "docs/05-operations/DHANHQ_ONE_YEAR_PLAN.json"
        ).read_bytes()
    )
    provider, calls = provider_for(p)
    app = create_app(
        settings_for_transient(db_engine.url.render_as_string(hide_password=False)),
        transient_provider_factory=lambda _: provider,
    )
    # No DB truncation here: the existing api fixture already restricts cleanup to *_test.
    with Session(db_engine) as db:
        before = [
            db.scalar(select(func.count()).select_from(model))
            for model in (Observation, ImportBatch, ImportRow, DataSource)
        ]
    with TestClient(app, headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}) as client:
        payload = {
            "plan": p.model_dump(mode="json"),
            "plan_fingerprint": APPROVED_FINGERPRINT,
            "live_approved": False,
        }
        assert (
            client.post("/api/v1/transient-session/dhan-history", json=payload).status_code == 403
        )
        assert not calls
        payload["live_approved"] = True
        result = client.post("/api/v1/transient-session/dhan-history", json=payload)
        assert result.status_code == 201, result.text
        data = result.json()["data"]
        assert len(calls) == 4 and len(data["instruments"]) == 4
        assert (
            client.post("/api/v1/transient-session/dhan-history", json=payload).status_code == 409
        )
        assert len(calls) == 4
        instruments = client.get("/api/v1/instruments", params={"limit": 2}).json()
        found = instruments["data"]
        cursor = instruments["meta"]["page"]["next_cursor"]
        while cursor:
            page = client.get("/api/v1/instruments", params={"limit": 2, "cursor": cursor}).json()
            found += page["data"]
            cursor = page["meta"]["page"]["next_cursor"]
        assert {x["symbol"] for x in found} == set(NAMES)
        assert len(client.get("/api/v1/data-sources").json()["data"]) == 1
        source = data["source_id"]
        ids = [x["instrument_id"] for x in data["instruments"]]
        params = {
            "source_id": source,
            "basis": "PROVIDER_ADJUSTED",
            "start": str(p.start),
            "end": str(p.end),
        }
        chart = client.get(f"/api/v1/instruments/{ids[0]}/chart", params=params)
        assert chart.status_code == 200 and len(chart.json()["data"]["points"]) == 247
        assert "TRANSIENT_ONLY_NO_PERSISTENCE" in chart.json()["meta"]["limitations"]
        assert chart.headers["cache-control"] == "no-store"
        for method, n in [("SMA", 20), ("SMA", 50), ("SMA", 200), ("EMA", 37), ("RSI", 14)]:
            response = client.get(
                f"/api/v1/instruments/{ids[0]}/indicators",
                params={**params, "indicator": method, "n": n},
            )
            assert response.status_code == 200
            assert response.json()["data"]["values"][-1]["value"] is not None
        history = client.get(
            f"/api/v1/instruments/{ids[0]}/history", params={**params, "limit": 10}
        )
        assert history.status_code == 200 and len(history.json()["data"]) == 10
        assert history.json()["meta"]["page"]["next_cursor"]
        for pair in ((0, 2), (1, 3)):
            compared = client.post(
                "/api/v1/comparisons",
                json={
                    "series": [
                        {
                            "instrument_id": ids[i],
                            "source_id": source,
                            "price_basis": "PROVIDER_ADJUSTED",
                        }
                        for i in pair
                    ],
                    "start": str(p.start),
                    "end": str(p.end),
                },
            )
            assert (
                compared.status_code == 200
                and compared.json()["data"]["common_observation_count"] == 247
            )
    with Session(db_engine) as db:
        after = [
            db.scalar(select(func.count()).select_from(model))
            for model in (Observation, ImportBatch, ImportRow, DataSource)
        ]
    assert before == after
