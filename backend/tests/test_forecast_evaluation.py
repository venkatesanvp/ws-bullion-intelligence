import ast
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.forecast_contracts import ForecastError, CorporateAction
from app.forecast_dataset import build_snapshot
from app.forecast_baselines import get_model
from app.forecast_evaluation import evaluate, EvaluationSpec, ModelRun
from .forecast_fixtures import dataset, spec
from .test_forecast_dataset import row_change, change


def execute(d, s):
    return evaluate(d, s, executed_at=s.evaluation_cutoff + timedelta(days=1))


def test_chronological_replay_matches_each_independent_origin_invocation():
    d = dataset()
    s = spec(d)
    r = execute(d, s)
    assert len(r.forecasts) == 9 and not r.exclusions
    assert (
        r.matured_unique_origins == r.max_disjoint_matured_windows == 3
        and r.overlapping_matured_window_pairs == 0
    )
    for evidence in r.forecasts:
        snap = build_snapshot(d, evidence.request)
        expected = get_model(evidence.request.model_id).predict(
            snap, evidence.request, created_at=r.executed_at
        )
        assert evidence.forecast == expected and evidence.metric_case is not None
        assert all(x.available_at <= evidence.request.cutoff for x in snap.observations)
    for e in r.evaluations:
        assert e.forecast_count == e.matured_count == 3 and e.failed_count == e.pending_count == 0
        if e.model_id == "B03":
            assert (
                e.metrics.price_mae is None
                and e.metrics.volatility_samples == 3
                and e.benchmark.paired_samples == 0
            )
        else:
            assert e.metrics.price_samples == e.benchmark.paired_samples == 3
    assert (
        r.retention == "TRANSIENT_MEMORY_ONLY" and r.classification == "SYNTHETIC_HISTORICAL_REPLAY"
    )


@pytest.mark.parametrize("horizon", [1, 5, 20, 60, 120])
def test_all_supported_horizons_with_matured_synthetic_labels(horizon):
    d = dataset(count=400)
    s = spec(d, indices=(5, 10, 15), horizon=horizon, evaluation_index=200)
    r = execute(d, s)
    assert all(e.matured_count == 3 for e in r.evaluations)
    assert all(
        x.forecast.target_session
        == d.calendar.sessions[
            d.calendar.sessions.index(
                next(t for t in d.calendar.sessions if t.session_date == x.request.origin_session)
            )
            + horizon
        ].session_date
        for x in r.forecasts
    )


def test_future_append_invariance_and_execution_timestamp_separation():
    d = dataset(count=60)
    s = spec(d)
    first = execute(d, s)
    shorter = change(d, observations=d.observations[:31])
    assert first == execute(shorter, s)
    changed = row_change(
        d, 40, open=Decimal(999), high=Decimal(999), low=Decimal(999), close=Decimal(999)
    )
    assert first == execute(changed, s)
    replay = evaluate(d, s, executed_at=first.executed_at + timedelta(days=1))
    assert first.experiment_id == replay.experiment_id and first.execution_id != replay.execution_id
    assert [f.forecast.forecast_id for f in first.forecasts] == [
        f.forecast.forecast_id for f in replay.forecasts
    ]
    assert [e.metrics for e in first.evaluations] == [e.metrics for e in replay.evaluations]


def test_pending_session_and_delayed_publication_not_scored_or_revealed():
    d = dataset()
    s = spec(d, indices=(25,), horizon=5, evaluation_index=28)
    r = execute(d, s)
    assert all(f.outcome_reason == "TARGET_SESSION_NOT_COMPLETE" for f in r.forecasts)
    assert all(e.pending_count == 1 and e.metrics.price_samples == 0 for e in r.evaluations)
    s = spec(d, indices=(5,), evaluation_index=10)
    late = row_change(d, 10, available_at=s.evaluation_cutoff + timedelta(days=1))
    r = execute(late, s)
    assert all(
        f.outcome_reason == "OUTCOME_PUBLICATION_PENDING"
        and f.outcome_fingerprint is None
        and f.metric_case is None
        for f in r.forecasts
    )
    assert all(e.pending_count == 1 for e in r.evaluations)


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("missing", "MISSING_OUTCOME_SESSION"),
        ("incomplete", "OUTCOME_QUALITY_FAILED"),
        ("quality", "OUTCOME_QUALITY_FAILED"),
        ("action", "UNADJUSTED_OUTCOME_ACTION"),
    ],
)
def test_outcome_quality_and_action_exclusions(defect, reason):
    d = dataset()
    s = spec(d, indices=(5,), evaluation_index=20)
    if defect == "missing":
        d = change(d, observations=d.observations[:8] + d.observations[9:])
    if defect == "incomplete":
        d = row_change(d, 8, completed=False)
    if defect == "quality":
        d = row_change(d, 8, quality="UNKNOWN")
    if defect == "action":
        d = change(
            d,
            corporate_actions=(
                CorporateAction(
                    effective_session=d.calendar.sessions[8].session_date,
                    available_at=d.calendar.sessions[7].close_at,
                    kind="SPLIT",
                    evidence_ref="SYNTHETIC_ACTION",
                ),
            ),
        )
    r = execute(d, s)
    assert all(f.outcome_reason == reason for f in r.forecasts)
    assert all(
        e.unavailable_outcome_count == 1 and e.metrics.price_mae is None for e in r.evaluations
    )


def test_missing_training_window_fails_without_omitting_exclusion_counts():
    d = dataset()
    d = change(d, observations=d.observations[:4] + d.observations[5:])
    s = spec(d, indices=(5, 10))
    r = execute(d, s)
    assert len(r.exclusions) == 3
    assert all(e.failed_count == 1 and e.matured_count == 1 for e in r.evaluations)


def test_after_assessment_origin_and_short_model_history_reported():
    d = dataset()
    s = spec(d, indices=(5, 25), evaluation_index=20, lookback=1)
    r = execute(d, s)
    assert sum(f.reason == "ORIGIN_AFTER_EVALUATION_CUTOFF" for f in r.exclusions) == 3
    assert sum(f.reason == "INSUFFICIENT_MODEL_HISTORY" for f in r.exclusions) == 2
    assert len(r.forecasts) == 1


def test_overlap_policy_reports_dependence_and_can_reject_overlap():
    d = dataset()
    s = spec(d, indices=(5, 6, 7))
    r = execute(d, s)
    assert r.overlapping_matured_window_pairs == 3 and r.max_disjoint_matured_windows == 1
    assert "OVERLAPPING_ERRORS_ARE_DEPENDENT" in r.warnings
    s = EvaluationSpec.model_validate(
        {**s.model_dump(), "overlap_policy": "REQUIRE_NONOVERLAPPING"}
    )
    with pytest.raises(ForecastError, match="OVERLAPPING_EVALUATION_ORIGINS"):
        execute(d, s)


@pytest.mark.parametrize(
    "defect", ["origins_reverse", "duplicate_origin", "duplicate_model", "horizon", "bounds"]
)
def test_evaluation_contract_rejects_ambiguous_or_excess_runs(defect):
    d = dataset()
    s = spec(d)
    v = s.model_dump()
    if defect == "origins_reverse":
        v["origins"] = tuple(reversed(s.origins))
    if defect == "duplicate_origin":
        v["origins"] = (s.origins[0], s.origins[0])
    if defect == "duplicate_model":
        v["models"] = (ModelRun(model_id="B01"), ModelRun(model_id="B01"))
    if defect == "horizon":
        v["horizon"] = True
    if defect == "bounds":
        v["origins"] = s.origins * 100
    with pytest.raises(ValidationError):
        EvaluationSpec.model_validate(v)


def test_model_configuration_and_input_changes_invalidate_experiment_identity():
    d = dataset()
    s = spec(d)
    base = execute(d, s)
    changed = row_change(
        d, 8, open=Decimal(100), high=Decimal(100), low=Decimal(100), close=Decimal(100)
    )
    assert execute(changed, s).experiment_id != base.experiment_id
    with pytest.raises(ForecastError, match="EXECUTION_BEFORE_ASSESSMENT_CUTOFF"):
        evaluate(d, s, executed_at=s.evaluation_cutoff - timedelta(seconds=1))


def test_forecasting_components_have_no_provider_database_environment_or_file_access(monkeypatch):
    import httpx
    import socket
    import sqlalchemy
    import builtins

    d = dataset()
    s = spec(d)

    def forbidden(*args, **kwargs):
        raise AssertionError("UNAUTHORIZED_IO")

    monkeypatch.setattr(httpx.Client, "request", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(sqlalchemy, "create_engine", forbidden)
    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    assert execute(d, s).forecasts


def test_module_import_architecture_and_no_runtime_registration():
    root = Path(__file__).resolve().parents[1] / "app"
    forbidden = {
        "os",
        "httpx",
        "requests",
        "sqlalchemy",
        "subprocess",
        "socket",
        "torch",
        "numpy",
        "pandas",
    }
    for path in (
        root / name
        for name in (
            "forecast_contracts.py",
            "forecast_dataset.py",
            "forecast_baselines.py",
            "forecast_metrics.py",
            "forecast_evaluation.py",
            "forecast_market_contracts.py",
        )
    ):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        assert not any(i and i.split(".")[0] in forbidden for i in imports)
        assert not any(
            i
            and any(k in i for k in ("dhan", "models", "config", "market_session", "transient_uat"))
            for i in imports
        )
    assert "register_forecast_research" in (root / "main.py").read_text(encoding="utf-8")
