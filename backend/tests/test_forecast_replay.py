"""Independent mode isolation and fixed-vintage replay tests; all prices are synthetic."""

from copy import copy
from datetime import timedelta
from decimal import Decimal, localcontext
from fractions import Fraction
from threading import Event
import pytest
from pydantic import ValidationError
from app.forecast_market_adapter import adapt
from app.forecast_contracts import ForecastError, fingerprint, CorporateAction
from app.forecast_dataset import build_snapshot
from app.forecast_baselines import get_model
from app.forecast_evaluation import (
    EvaluationSpec,
    MarketEvaluationSpec,
    ReplayEvaluationSpec,
    ForecastOrigin,
    ModelRun,
    evaluate,
)
from app.forecast_replay import ReplayRequest, ReplaySnapshot, POLICY, MODE, replay_snapshot
from app.forecast_research_service import ResearchOptions
from .forecast_research_fixtures import service_fixture
from .forecast_fixtures import dataset as synthetic_dataset


def prepared(*, late=True, count=180, index=0):
    s, reader, b, ref, clock, ticks, cal = service_fixture(count, index=index)
    i, source, rows = reader()
    if late:
        source.reviewed_at = clock[0] - timedelta(hours=1)
        cal = cal.model_copy(update={"known_at": clock[0] - timedelta(hours=1)})
        updated = []
        for old in rows:
            r = copy(old)
            r.ingested_at = clock[0] - timedelta(minutes=30)
            updated.append(r)
        ref[0] = (i, source, tuple(updated))
        s.calendar_override = cal
    d = adapt(
        *reader(), listings=s.market.provider.listings(), now=clock[0], calendar_override=cal
    ).dataset
    return s, reader, b, ref, clock, cal, d


def spec(d, now, *, conditional=True, horizon=5, indices=(100, 105, 110), lookback=60, **kw):
    cls = ReplayEvaluationSpec if conditional else MarketEvaluationSpec
    return cls(
        horizon=horizon,
        lookback=lookback,
        origins=tuple(
            ForecastOrigin(
                session=d.calendar.sessions[k].session_date,
                cutoff=d.calendar.sessions[k].close_at + timedelta(minutes=30),
            )
            for k in indices
        ),
        models=tuple(ModelRun(model_id=m) for m in ("B01", "B02", "B03")),
        evaluation_cutoff=now,
        **({"assumption_policy": POLICY} if conditional else {}),
        **kw,
    )


def replay(d, now, **kwargs):
    return evaluate(d, spec(d, now, **kwargs), executed_at=now)


@pytest.mark.parametrize("index", range(4))
@pytest.mark.parametrize("horizon", (1, 5, 20))
def test_four_synthetic_instrument_contracts_replay_common_origins_with_preserved_first_seen(
    index, horizon
):
    *_, clock, cal, d = prepared(index=index)
    before = fingerprint(d)
    strict = evaluate(
        d, spec(d, clock[0], conditional=False, horizon=horizon), executed_at=clock[0]
    )
    r = replay(d, clock[0], horizon=horizon)
    assert strict.evaluation_mode == "STRICT_POINT_IN_TIME" and strict.matured_unique_origins == 0
    assert {f.reason for f in strict.exclusions} == {"METADATA_NOT_AVAILABLE"}
    assert r.evaluation_mode == r.classification == MODE and r.assumption_policy == POLICY
    assert r.matured_unique_origins == 3 and not r.exclusions
    assert all(x.matured_count == 3 for x in r.evaluations)
    assert r.evaluations[2].metrics.directional_hit_rate is None
    assert (
        r.evaluations[0].benchmark.paired_samples == r.evaluations[1].benchmark.paired_samples == 3
    )
    assert r.evaluations[2].benchmark.paired_samples == 0 and fingerprint(d) == before
    for e in r.forecasts:
        assert e.forecast.last_availability_at > e.forecast.cutoff
        assert e.forecast.last_observation_at is None and e.forecast.created_at == clock[0]
        assert (
            e.forecast.evaluation_mode == MODE
            and e.forecast.provenance.known_at == d.provenance.known_at
        )


@pytest.mark.parametrize("horizon", (60, 120))
def test_long_horizons_require_actual_contiguous_input_and_outcome_calendar_support(horizon):
    *_, clock, cal, d = prepared(count=300)
    r = replay(d, clock[0], horizon=horizon, indices=(100,))
    assert r.matured_unique_origins == 1
    short = d.model_copy(update={"observations": d.observations[:120]})
    r = replay(short, clock[0], horizon=horizon, indices=(100,))
    assert r.matured_unique_origins == 0 and all(
        f.outcome_reason == "MISSING_OUTCOME_SESSION" for f in r.forecasts
    )


def test_future_target_prices_change_only_outcomes_not_earlier_prediction_or_context_fingerprint():
    *_, clock, cal, d = prepared()
    a = replay(d, clock[0], indices=(100,))
    rows = list(d.observations)
    for k in range(101, len(rows)):
        p = rows[k]
        rows[k] = p.model_copy(
            update={
                "open": p.open * 2,
                "high": p.high * 2,
                "low": p.low * 2,
                "close": p.close * 2,
                "canonical_hash": "a" * 64,
            }
        )
    b = replay(d.model_copy(update={"observations": tuple(rows)}), clock[0], indices=(100,))
    assert a.experiment_id != b.experiment_id
    assert [
        (
            x.forecast.forecast_id,
            x.forecast.dataset_fingerprint,
            x.forecast.predicted_price,
            x.forecast.horizon_volatility,
        )
        for x in a.forecasts
    ] == [
        (
            x.forecast.forecast_id,
            x.forecast.dataset_fingerprint,
            x.forecast.predicted_price,
            x.forecast.horizon_volatility,
        )
        for x in b.forecasts
    ]
    assert a.forecasts[0].metric_case.actual_price != b.forecasts[0].metric_case.actual_price


def test_replay_cannot_be_reinterpreted_as_strict_and_preserves_original_nulls():
    *_, clock, cal, d = prepared()
    origin = d.calendar.sessions[100]
    q = ReplayRequest(
        instrument=d.instrument,
        origin_session=origin.session_date,
        horizon=5,
        lookback=60,
        model_id="B01",
        cutoff=origin.close_at + timedelta(minutes=30),
        assessment_cutoff=clock[0],
        assumption_policy=POLICY,
    )
    snap = replay_snapshot(d, q)
    assert snap.observations[-1].available_at == d.observations[100].available_at
    assert snap.observations[-1].source_event_at is None
    with pytest.raises(ForecastError):
        build_snapshot(d, q)
    from app.forecast_market_contracts import MarketSnapshot

    with pytest.raises(ValidationError):
        MarketSnapshot.model_validate(snap.model_dump())
    with pytest.raises(ValidationError):
        ReplaySnapshot.model_validate({**snap.model_dump(), "assessment_cutoff": origin.close_at})
    with pytest.raises(ForecastError):
        get_model("B01").predict(snap, q, created_at=clock[0] - timedelta(seconds=1))


@pytest.mark.parametrize(
    "missing,reason", [(90, "MISSING_OR_UNAVAILABLE_SESSION"), (105, "MISSING_OUTCOME_SESSION")]
)
def test_missing_context_and_target_sessions_not_filled(missing, reason):
    *_, clock, cal, d = prepared()
    r = replay(
        d.model_copy(
            update={"observations": tuple(x for j, x in enumerate(d.observations) if j != missing)}
        ),
        clock[0],
        indices=(100,),
    )
    assert r.matured_unique_origins == 0
    assert (
        {x.reason for x in r.exclusions} == {reason}
        if missing == 90
        else {x.outcome_reason for x in r.forecasts} == {reason}
    )


@pytest.mark.parametrize(
    "lookback,reason", [(1, "INSUFFICIENT_MODEL_HISTORY"), (1000, "INSUFFICIENT_LOOKBACK")]
)
def test_model_minima_and_context_history_not_relaxed(lookback, reason):
    *_, clock, cal, d = prepared()
    r = replay(d, clock[0], lookback=lookback, indices=(100,))
    assert reason in {x.reason for x in r.exclusions}
    if lookback == 1:
        assert r.evaluations[0].matured_count == 1 and r.evaluations[1].matured_count == 0


@pytest.mark.parametrize(
    "kind", ("declared_break", "action", "special_target", "future_first_seen", "incomplete")
)
def test_structural_and_quality_failures_remain_excluded(kind):
    *_, clock, cal, d = prepared()
    kw = {}
    if kind == "declared_break":
        kw["known_break_sessions"] = (cal.sessions[95].session_date,)
    if kind == "action":
        d = d.model_copy(
            update={
                "corporate_actions": (
                    CorporateAction(
                        effective_session=cal.sessions[95].session_date,
                        available_at=clock[0],
                        kind="SPLIT",
                        evidence_ref="SYNTHETIC ACTION",
                    ),
                )
            }
        )
    if kind == "special_target":
        kw["blocked_target_sessions"] = (cal.sessions[105].session_date,)
    if kind in ("future_first_seen", "incomplete"):
        rows = list(d.observations)
        rows[95] = rows[95].model_copy(
            update={"available_at": clock[0] + timedelta(hours=1)}
            if kind == "future_first_seen"
            else {"completed": False}
        )
        d = d.model_copy(update={"observations": tuple(rows)})
    r = replay(d, clock[0], indices=(100,), **kw)
    assert r.matured_unique_origins == 0 and len(r.exclusions) == 3


@pytest.mark.parametrize("basis", ("RAW_CLOSE", "PIT_ADJUSTED_CLOSE"))
def test_replay_does_not_relabel_or_unadjust_provider_prices(basis):
    *_, clock, cal, d = prepared()
    with pytest.raises(ForecastError):
        replay(d.model_copy(update={"basis": basis}), clock[0])


def test_independent_fraction_and_high_precision_replay_metrics_and_b03_separation():
    *_, clock, cal, d = prepared()
    r = replay(d, clock[0], indices=(100, 105, 110))

    def dec(f):
        return Decimal(f.numerator) / Decimal(f.denominator)

    with localcontext() as ctx:
        ctx.prec = 100
        expected = {}
        for model in ("B01", "B02"):
            errors = []
            return_errors = []
            hits = 0
            for k in (100, 105, 110):
                closes = [Fraction(x.close) for x in d.observations[k - 59 : k + 1]]
                returns = [b / a - 1 for a, b in zip(closes, closes[1:])]
                factor = Fraction(1) if model == "B01" else (1 + sum(returns) / len(returns)) ** 5
                pred = dec(closes[-1] * factor).quantize(Decimal("1e-12"))
                ret = dec(factor - 1).quantize(Decimal("1e-12"))
                actual = d.observations[k + 5].close
                actual_return = actual / d.observations[k].close - 1
                errors.append(pred - actual)
                return_errors.append(ret - actual_return)
                hits += ((ret > 0) - (ret < 0)) == ((actual_return > 0) - (actual_return < 0))
            expected[model] = (
                sum(abs(x) for x in errors) / 3,
                (sum(x * x for x in errors) / 3).sqrt(),
                sum(errors) / 3,
                sum(abs(x) for x in return_errors) / 3,
                Decimal(hits) / 3,
            )
        for e in r.evaluations[:2]:
            for actual, reference in zip(
                (
                    e.metrics.price_mae,
                    e.metrics.price_rmse,
                    e.metrics.price_bias,
                    e.metrics.return_mae,
                    e.metrics.directional_hit_rate,
                ),
                expected[e.model_id],
            ):
                assert abs(actual - reference) <= Decimal("1e-12")
        b03 = r.evaluations[2]
        assert b03.metrics.price_samples == 0 and b03.metrics.volatility_samples == 3
        errors = []
        for k in (100, 105, 110):
            cs = [Fraction(x.close) for x in d.observations[k - 59 : k + 1]]
            rs = [b / a - 1 for a, b in zip(cs, cs[1:])]
            mean = sum(rs) / len(rs)
            var = sum((x - mean) ** 2 for x in rs) / (len(rs) - 1)
            sigma = (dec(var).sqrt() * Decimal(5).sqrt()).quantize(Decimal("1e-12"))
            path = [Fraction(x.close) for x in d.observations[k : k + 6]]
            future = [b / a - 1 for a, b in zip(path, path[1:])]
            rv = dec(sum(x * x for x in future)).sqrt()
            errors.append(sigma - rv)
        assert abs(b03.metrics.volatility_proxy_mae - sum(abs(x) for x in errors) / 3) <= Decimal(
            "1e-12"
        )


def test_overlapping_errors_disclosed_and_nonoverlap_policy_preserved():
    *_, clock, cal, d = prepared()
    r = replay(d, clock[0], indices=(100, 101, 102))
    assert r.overlapping_matured_window_pairs == 3 and r.max_disjoint_matured_windows == 1
    with pytest.raises(ForecastError, match="OVERLAPPING"):
        replay(d, clock[0], indices=(100, 101), overlap_policy="REQUIRE_NONOVERLAPPING")


def test_synthetic_mode_stays_deterministic_and_cannot_use_real_replay_contract():
    d = synthetic_dataset()
    now = d.observations[-1].available_at + timedelta(days=1)
    origin = d.calendar.sessions[100]
    s = EvaluationSpec(
        horizon=5,
        lookback=60,
        origins=(
            ForecastOrigin(
                session=origin.session_date, cutoff=origin.close_at + timedelta(minutes=30)
            ),
        ),
        models=(ModelRun(model_id="B01"),),
        evaluation_cutoff=now,
    )
    a = evaluate(d, s, executed_at=now)
    b = evaluate(d, s, executed_at=now)
    assert a == b and a.evaluation_mode == "SYNTHETIC"
    with pytest.raises(ForecastError):
        evaluate(
            d,
            ReplayEvaluationSpec.model_validate(
                {
                    **s.model_dump(),
                    "evaluation_mode": MODE,
                    "quality": {"quality": "CONDITIONAL_OWNER_RESEARCH"},
                    "assumption_policy": POLICY,
                }
            ),
            executed_at=now,
        )


@pytest.mark.parametrize(
    "mode,ack,policy,reason",
    [
        (MODE, False, None, "CONDITIONAL_REPLAY_ACKNOWLEDGEMENT_REQUIRED"),
        ("SYNTHETIC", False, None, "EVALUATION_MODE_SOURCE_MISMATCH"),
        ("STRICT_POINT_IN_TIME", True, POLICY, "REPLAY_ASSUMPTIONS_INVALID_FOR_MODE"),
    ],
)
def test_service_requires_explicit_ack_and_mode_compatible_with_source(mode, ack, policy, reason):
    s, reader, b, ref, clock, cal, d = prepared()
    body = ResearchOptions(
        **{
            **b.model_dump(),
            "start": cal.sessions[100].session_date,
            "end": cal.sessions[110].session_date,
            "evaluation_mode": mode,
            "acknowledge_replay_assumptions": ack,
            "replay_policy": policy,
        }
    )
    with pytest.raises(ForecastError, match=reason):
        s.work("evaluate", reader, body, Event())


def test_api_service_modes_do_not_change_current_forecast_or_canonical_provenance():
    s, reader, b, ref, clock, cal, d = prepared()
    base = s.work("run", reader, b, Event())
    args = {
        **b.model_dump(),
        "start": cal.sessions[100].session_date,
        "end": cal.sessions[110].session_date,
    }
    strict = s.work("evaluate", reader, ResearchOptions(**args), Event())
    conditional = s.work(
        "evaluate",
        reader,
        ResearchOptions(
            **{
                **args,
                "evaluation_mode": MODE,
                "acknowledge_replay_assumptions": True,
                "replay_policy": POLICY,
            }
        ),
        Event(),
    )
    again = s.work("run", reader, b, Event())
    assert strict["sample_count"] == 0 and conditional["sample_count"] == 3
    assert (
        strict["evaluation_mode"] == "STRICT_POINT_IN_TIME"
        and conditional["evaluation_mode"] == MODE
    )
    assert strict["experiment"]["experiment_id"] != conditional["experiment"]["experiment_id"]
    assert base["results"] == again["results"]
    assert all(x["evaluation_mode"] == MODE for x in conditional["rows"])
    assert (
        "UNVERIFIED"
        == conditional["context"]["qualification"]["availability"][
            "historical_provider_publication"
        ]
    )
