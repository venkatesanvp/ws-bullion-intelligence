from copy import copy
from datetime import timedelta
from threading import Event
import pytest
from pydantic import ValidationError
from app.forecast_contracts import ForecastError
from app.forecast_research_service import ResearchOptions
from .forecast_research_fixtures import service_fixture, canonical_input


def test_current_real_baselines_share_snapshot_and_research_semantics():
    s, reader, body, _, clock, _, _ = service_fixture()
    r = s.work("run", reader, body, Event())
    assert r["status"] == "AVAILABLE" and len(r["results"]) == 3
    result = {x["model_id"]: x["forecast"] for x in r["results"]}
    assert (
        result["B01"]["predicted_price"] == r["context"]["last_close"]
        and result["B02"]["predicted_price"] is not None
    )
    assert (
        result["B03"]["predicted_price"] is result["B03"]["predicted_return"] is None
        and result["B03"]["horizon_volatility"] is not None
    )
    assert len({x["dataset_fingerprint"] for x in result.values()}) == 1
    assert all(x["calibration_status"] == "NOT_SUPPORTED" for x in result.values())


def test_real_walk_forward_bias_common_samples_and_no_historical_backdating():
    s, reader, b, _, clock, _, cal = service_fixture()
    body = ResearchOptions(
        **{
            **b.model_dump(),
            "start": cal.sessions[100].session_date,
            "end": cal.sessions[130].session_date,
            "frequency": 5,
        }
    )
    r = s.work("evaluate", reader, body, Event())
    assert r["sample_count"] == 7 and r["status"] == "AVAILABLE"
    metrics = {x["model_id"]: x for x in r["experiment"]["evaluations"]}
    assert metrics["B01"]["matured_count"] == metrics["B02"]["matured_count"] == 7
    assert (
        metrics["B01"]["metrics"]["price_bias"] is not None
        and metrics["B02"]["metrics"]["return_bias"] is not None
    )
    assert (
        metrics["B03"]["metrics"]["directional_hit_rate"] is None
        and metrics["B03"]["benchmark"]["paired_samples"] == 0
    )
    assert all(x["created_at"] > x["cutoff"] for x in r["rows"])


def test_historical_evaluation_reports_excluded_first_seen_cutoffs_without_fake_accuracy():
    s, reader, b, ref, clock, _, cal = service_fixture()
    i, source, rows = reader()
    rs = []
    for old in rows:
        r = copy(old)
        r.ingested_at = clock[0]
        rs.append(r)
    ref[0] = (i, source, tuple(rs))
    body = ResearchOptions(
        **{
            **b.model_dump(),
            "start": cal.sessions[100].session_date,
            "end": cal.sessions[130].session_date,
            "frequency": 5,
        }
    )
    r = s.work("evaluate", reader, body, Event())
    assert (
        r["sample_count"] == 0
        and r["status"] == "DATA_QUALITY_BLOCKED"
        and len(r["exclusions"]) == 21
    )
    assert all(
        e["metrics"]["price_mae"] is None and e["metrics"]["directional_hit_rate"] is None
        for e in r["experiment"]["evaluations"]
    )


def test_pending_tracking_matures_only_with_later_available_final_data_without_rewriting():
    s, reader, b, ref, clock, _, cal = service_fixture()
    run = s.work("run", reader, b, Event())
    rid = run["run_id"]
    before = [r["forecast"]["forecast_id"] for r in run["results"]]
    t = s.work("track", reader, b, Event(), run_id=rid)
    assert all(r["status"] == "PENDING" for r in t["tracking"])
    i, source, rows, _ = canonical_input(count=190)
    ref[0] = (i, source, rows)
    clock[0] = cal.sessions[189].close_at + timedelta(days=1, hours=1)
    t = s.work("track", reader, b, Event(), run_id=rid)
    assert all(r["status"] == "EVALUATED" for r in t["tracking"])
    assert (
        t["tracking"][2]["price_error"] is None
        and t["tracking"][2]["volatility_proxy_error"] is not None
    )
    assert [r["forecast"]["forecast_id"] for r in s._runs[rid]["payload"]["results"]] == before


def test_tracking_revisions_expiry_and_capacity_limits():
    s, reader, b, ref, clock, ticks, _ = service_fixture()
    run = s.work("run", reader, b, Event())
    rid = run["run_id"]
    i, source, rows = reader()
    rs = list(rows)
    r = copy(rs[-1])
    r.canonical_hash = "revised"
    rs[-1] = r
    ref[0] = (i, source, tuple(rs))
    t = s.work("track", reader, b, Event(), run_id=rid)
    assert all(x["status"] == "DATA_QUALITY_BLOCKED" for x in t["tracking"])
    ticks[0] = s._runs[rid]["expires_at"] + 1
    with pytest.raises(ForecastError, match="NOT_FOUND_OR_EXPIRED"):
        s.identifiers(rid)
    assert not s.receipts()


def test_resource_controls_cancellation_busy_origin_limit_rate_limit_and_revision():
    s, reader, b, _, _, ticks, cal = service_fixture()
    cancel = Event()
    cancel.set()
    with pytest.raises(ForecastError, match="CANCELLED"):
        s.work("run", reader, b, cancel)
    s._gate.acquire()
    with pytest.raises(ForecastError, match="BUSY"):
        s.work("run", reader, b, Event())
    s._gate.release()
    wrong = ResearchOptions(**{**b.model_dump(), "expected_revision": "0" * 64})
    with pytest.raises(ForecastError, match="SNAPSHOT_CHANGED"):
        s.work("run", reader, wrong, Event())
    large = ResearchOptions(
        **{
            **b.model_dump(),
            "start": cal.sessions[1].session_date,
            "end": cal.sessions[130].session_date,
            "frequency": 1,
        }
    )
    with pytest.raises(ForecastError, match="ORIGIN_LIMIT"):
        s.work("evaluate", reader, large, Event())
    s._calls.clear()
    s._calls.extend([ticks[0]] * 30)
    with pytest.raises(ForecastError, match="RATE_LIMITED"):
        s.work("run", reader, b, Event())


def test_timeout_releases_compute_lock():
    s, reader, b, _, _, ticks, _ = service_fixture()

    def advance():
        ticks[0] += 6
        return ticks[0]

    s.monotonic = advance
    with pytest.raises(ForecastError, match="TIMEOUT"):
        s.work("run", reader, b, Event())
    assert s._gate.acquire(blocking=False)
    s._gate.release()


@pytest.mark.parametrize(
    "values",
    [
        {"horizon": True},
        {"horizon": 2},
        {"lookback": 1001},
        {"models": []},
        {"models": ["B03", "B03"]},
        {"models": ["KRONOS"]},
        {"annualization_sessions": True},
    ],
)
def test_request_bounds(values):
    _, _, body, *_ = service_fixture()
    with pytest.raises(ValidationError):
        ResearchOptions(**{**body.model_dump(), **values})


def test_tracking_retention_covers_maturity_reopens_original_evidence_and_is_capacity_bounded():
    s, reader, b, _, clock, ticks, cal = service_fixture(count=5)
    b = ResearchOptions(**{**b.model_dump(), "lookback": 1, "models": ["B01"]})
    ids = []
    for _ in range(35):
        ticks[0] += 61
        ids.append(s.work("run", reader, b, Event())["run_id"])
    assert len(s.receipts()) == 32
    with pytest.raises(ForecastError, match="NOT_FOUND_OR_EXPIRED"):
        s.identifiers(ids[0])
    rid = ids[-1]
    original = s._runs[rid]["payload"]["results"][0]["forecast"]["forecast_id"]
    assert s._runs[rid]["expires_at"] - ticks[0] > 7 * 86400
    out = s.work("track", reader, b, Event(), run_id=rid)
    assert out["original_run"]["results"][0]["forecast"]["forecast_id"] == original
    assert out["original_run"]["context"]["history"]


def test_real_evaluation_excludes_unqualified_special_target_timing():
    from app.forecast_market_adapter import adapt
    from app.forecast_evaluation import MarketEvaluationSpec, ForecastOrigin, ModelRun, evaluate

    s, reader, b, _, clock, _, cal = service_fixture()
    i, source, rows = reader()
    data = adapt(
        i, source, rows, listings=s.market.provider.listings(), now=clock[0], calendar_override=cal
    ).dataset
    spec = MarketEvaluationSpec(
        horizon=5,
        lookback=20,
        origins=(
            ForecastOrigin(
                session=cal.sessions[60].session_date,
                cutoff=cal.sessions[60].close_at + timedelta(minutes=30),
            ),
        ),
        models=(ModelRun(model_id="B01"),),
        evaluation_cutoff=clock[0],
        blocked_target_sessions=(cal.sessions[65].session_date,),
    )
    result = evaluate(data, spec, executed_at=clock[0])
    assert (
        result.exclusions[0].reason == "TARGET_SESSION_TIMING_UNQUALIFIED"
        and result.evaluations[0].metrics.price_mae is None
    )
