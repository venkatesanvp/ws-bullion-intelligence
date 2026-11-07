"""Synthetic exact-reference tests for performance, samples and cutoff-based regimes."""

from datetime import timedelta
from decimal import Decimal, localcontext
from fractions import Fraction
from types import SimpleNamespace as NS
from threading import Event
import pytest
from pydantic import ValidationError
from app.forecast_contracts import ForecastError
from app.forecast_dataset import build_snapshot
from app.forecast_evaluation import evaluate
from app.forecast_baselines import get_model
from app.forecast_metrics import MetricCase
from app.forecast_performance import analyze, distribution, error_values, compatible_cards, windows
from app.forecast_performance_contracts import (
    PerformanceAnalysis,
    PerformanceResult,
    SampleEvidence,
)
from app.forecast_regimes import classify
from .forecast_fixtures import dataset, spec, request
from .test_forecast_replay import prepared, spec as real_spec


def experiment(
    *, indices=(30, 35, 40), horizon=5, models=("B01", "B02", "B03"), lookback=21, regimes=True
):
    d = dataset(count=100)
    s = spec(
        d, indices=indices, horizon=horizon, models=models, lookback=lookback, evaluation_index=90
    )
    r = evaluate(d, s, executed_at=s.evaluation_cutoff + timedelta(days=1), regime_analysis=regimes)
    return d, r


def analysis(d, r, **kw):
    return analyze(
        r,
        instrument=d.instrument,
        basis=d.basis,
        calendar=d.calendar,
        descriptors={m.model_id: get_model(m.model_id).descriptor for m in r.spec.models},
        start=r.spec.origins[0].session,
        end=r.spec.origins[-1].session,
        qualification="SYNTHETIC_TEST_ONLY",
        limitations=("SYNTHETIC_PRICES_NOT_MARKET_EVIDENCE",),
        **kw,
    )


def test_independent_error_values_rolling_distribution_and_model_separation():
    d, r = experiment(indices=(30, 31, 32, 33))
    a = analysis(d, r, rolling_window=3)
    assert len(a.cards) == 3 and a.comparison.common_origins == 4 and len(a.errors) == 12
    for card in a.cards:
        assert (
            card.model_version == "baseline-simple-v1"
            and card.samples.effective_independent_count is None
        )
        assert card.samples.overlapping_pairs == 6 and card.samples.disjoint_windows == 1
        cases = [e.metric_case for e in r.forecasts if e.forecast.model.model_id == card.model_id]
        with localcontext() as ctx:
            ctx.prec = 100
            raw = []
            for case in cases:
                er = next(x for x in a.errors if x.forecast_id == case.case_id)
                if case.predicted_price is not None:
                    exact = Fraction(case.predicted_price) - Fraction(case.actual_price)
                    val = Decimal(exact.numerator) / Decimal(exact.denominator)
                    pct = 100 * exact / Fraction(case.actual_price)
                    ret = Fraction(case.predicted_return) - (
                        Fraction(case.actual_price) / Fraction(case.origin_price) - 1
                    )
                    assert abs(er.signed_error - val) <= Decimal("1e-12") and abs(
                        er.absolute_error - abs(val)
                    ) <= Decimal("1e-12")
                    assert abs(
                        er.percentage_error - Decimal(pct.numerator) / Decimal(pct.denominator)
                    ) <= Decimal("1e-12")
                    assert abs(
                        er.return_error - Decimal(ret.numerator) / Decimal(ret.denominator)
                    ) <= Decimal("1e-12")
                else:
                    val = case.predicted_volatility - case.realized_volatility
                    assert er.percentage_error is er.return_error is None
                raw.append(val)
            rolling = [x for x in a.rolling if x.model_id == card.model_id]
            assert [x.sample_count for x in rolling] == [1, 2, 3, 3] and [
                x.partial_window for x in rolling
            ] == [True, True, False, False]
            tail = raw[-3:]
            assert abs(rolling[-1].mae - sum(abs(x) for x in tail) / 3) <= Decimal("1e-12")
            assert abs(rolling[-1].rmse - (sum(x * x for x in tail) / 3).sqrt()) <= Decimal("1e-12")
            assert abs(rolling[-1].bias - sum(tail) / 3) <= Decimal("1e-12")
            assert rolling[-1].outcome_known_at > r.spec.origins[-1].cutoff
    assert (
        a.cards[2].metric_kind == "VOLATILITY_PROXY"
        and a.cards[2].metrics.directional_hit_rate is None
    )
    assert [x.unit for x in a.distributions] == [
        "RETURN_ERROR_FRACTION",
        "RETURN_ERROR_FRACTION",
        "VOLATILITY_PROXY_FRACTION",
    ]
    assert all(sum(b.count for b in x.bins) == x.sample_count == 4 for x in a.distributions)


@pytest.mark.parametrize(
    "actual,origin,reason",
    [
        (Decimal(0), Decimal(0), "ZERO_OR_NEAR_ZERO_ACTUAL_PERCENTAGE_UNAVAILABLE"),
        (Decimal("1e-12"), Decimal("1e-8"), "ZERO_OR_NEAR_ZERO_ORIGIN_RETURN_ERROR_UNAVAILABLE"),
        (Decimal("1e-8"), Decimal("1e-12"), "ZERO_OR_NEAR_ZERO_ACTUAL_PERCENTAGE_UNAVAILABLE"),
    ],
)
def test_zero_near_zero_prices_never_substitute_epsilon(actual, origin, reason):
    c = NS(
        predicted_price=Decimal("1"),
        actual_price=actual,
        origin_price=origin,
        predicted_return=Decimal(0),
    )
    signed, pct, ret, limits, unit = error_values(c)
    assert pct is ret is None and reason in limits and signed == 1 - actual
    if not actual:
        with pytest.raises(ValidationError):
            MetricCase(
                case_id="synthetic",
                instrument_id="synthetic",
                origin_session=dataset().observations[0].session_date,
                target_session=dataset().observations[1].session_date,
                origin_price="1",
                actual_price="0",
                realized_volatility="0",
                predicted_price="1",
                predicted_return="0",
                predicted_volatility=None,
            )


def test_fixed_distribution_boundaries_nearest_rank_and_empty_no_probabilities():
    values = tuple(Decimal(x) for x in ("-.06", "-.05", "-.01", "0", ".01", ".05", ".06"))
    a = distribution("SYNTHETIC_MODEL", values, 2, "RETURN_ERROR_FRACTION")
    assert (
        [x.count for x in a.bins] == [1] * 7
        and (a.p10, a.median, a.p90) == (Decimal("-.06"), Decimal(0), Decimal(".06"))
        and a.excluded_count == 2
    )
    b = distribution("SYNTHETIC_MODEL", (), 0, "RETURN_ERROR_FRACTION")
    assert b.median is b.p10 is b.p90 is None
    assert not hasattr(a, "probability_positive")


def test_common_origins_exclude_unmatched_and_do_not_compare_incompatible_targets():
    d, r = experiment()
    forecasts = list(r.forecasts)
    lost = next(e for e in forecasts if e.forecast.model.model_id == "B02")
    forecasts = [
        e.model_copy(
            update={
                "outcome_status": "UNAVAILABLE",
                "outcome_reason": "SYNTHETIC_MISSING_OUTCOME",
                "metric_case": None,
            }
        )
        if e == lost
        else e
        for e in forecasts
    ]
    summaries = tuple(
        e.model_copy(update={"matured_count": 2, "unavailable_outcome_count": 1})
        if e.model_id == "B02"
        else e
        for e in r.evaluations
    )
    altered = r.model_copy(update={"forecasts": tuple(forecasts), "evaluations": summaries})
    a = analysis(d, altered)
    first, second, vol = a.cards
    assert (
        a.comparison.common_origins == 2
        and first.samples.eligible_origins == 3
        and first.samples.scored_origins == 2
        and first.samples.unmatched_origins == 1
    )
    assert (
        second.samples.scored_origins == 2
        and second.samples.unavailable_outcomes == 1
        and vol.samples.scored_origins == 3
    )
    assert first.origin_set_fingerprint == second.origin_set_fingerprint
    b = next(e for e in forecasts if e.forecast.model.model_id == "B02" and e.metric_case)
    bad = b.model_copy(
        update={
            "metric_case": b.metric_case.model_copy(
                update={"actual_price": b.metric_case.actual_price + 1}
            )
        }
    )
    with pytest.raises(ForecastError, match="INCOMPATIBLE_BENCHMARK_TARGETS"):
        analysis(
            d,
            altered.model_copy(
                update={"forecasts": tuple(bad if e == b else e for e in forecasts)}
            ),
        )


@pytest.mark.parametrize("models", [("B01",), ("B02",), ("B03",)])
def test_single_model_does_not_fabricate_pairwise_comparison(models):
    d, r = experiment(models=models)
    a = analysis(d, r)
    assert (
        a.comparison.common_origins == 0
        and a.comparison.b02_minus_b01_mae is None
        and a.cards[0].sample_basis == "MODEL_ELIGIBLE_ONLY"
    )


@pytest.mark.parametrize(
    "key,value",
    [
        ("evaluation_mode", "STRICT_POINT_IN_TIME"),
        ("horizon", 20),
        ("dataset_fingerprint", "changed"),
        ("basis", "other"),
        ("model_version", "other"),
    ],
)
def test_registry_contracts_reject_mixing_or_preserve_version_identity(key, value):
    d, r = experiment()
    a = analysis(d, r)
    card = a.cards[1]
    changed = PerformanceResult.model_validate({**card.model_dump(), key: value})
    if key == "model_version":
        assert changed.model_version != card.model_version
        return
    with pytest.raises((ValidationError, ForecastError)):
        PerformanceAnalysis.model_validate(
            {**a.model_dump(), "cards": (a.cards[0].model_dump(), changed.model_dump())}
        )
    with pytest.raises(ForecastError):
        compatible_cards([a.cards[0], changed])


def test_window_counts_are_exact_interval_counts_not_independent_sample_estimates():
    d, r = experiment(indices=(30, 31, 35, 40))
    cases = [x.metric_case for x in r.forecasts if x.forecast.model.model_id == "B01"]
    assert windows(cases, d.calendar) == (2, 3)
    a = analysis(d, r)
    assert a.cards[0].samples.independence_status == "NOT_ESTIMATED"
    with pytest.raises(ValidationError):
        SampleEvidence.model_validate(
            {**a.cards[0].samples.model_dump(), "effective_independent_count": 3}
        )


@pytest.mark.parametrize(
    "closes,trend,vol",
    [
        ([100] * 21, "SIDEWAYS", "LOW"),
        ([100 + i for i in range(21)], "TRENDING", "LOW"),
        ([100, 110] * 10 + [100], "SIDEWAYS", "HIGH"),
        ([100, 167.5] + [135] * 19, "TRENDING", "HIGH"),
        ([100, 167.45] + [134.9] * 19, "SIDEWAYS", "HIGH"),
        ([100] * 20 + [101.9999], "SIDEWAYS", "LOW"),
        ([100] * 20 + [102], "TRENDING", "LOW"),
    ],
)
def test_regime_rules_deterministic_thresholds_flat_and_two_axes(closes, trend, vol):
    d = dataset(closes=[str(x) for x in closes])
    q = request(d, index=20, lookback=21)
    s = build_snapshot(d, q)
    r = classify(s)
    assert (
        r.trend == trend
        and r.volatility == vol
        and r.input_count == 21
        and r.latest_input_available_at <= q.cutoff
    )
    assert r.context_fingerprint == s.fingerprint
    with localcontext() as ctx:
        ctx.prec = 100
        rs = [Decimal(str(b)) / Decimal(str(a)) - 1 for a, b in zip(closes, closes[1:])]
        mean = sum(rs) / 20
        reference = (sum((x - mean) ** 2 for x in rs) / 19).sqrt()
        assert abs(r.session_sigma - reference) <= Decimal("1e-12")


def test_optional_regimes_insufficient_context_and_future_perturbation_integrity():
    d = dataset(count=100)
    s = spec(d, indices=(30,), lookback=21, evaluation_index=90)
    base = evaluate(d, s, executed_at=s.evaluation_cutoff)
    a = evaluate(d, s, executed_at=s.evaluation_cutoff, regime_analysis=True)
    assert base.regime_rule_version is None and base.experiment_id != a.experiment_id
    assert [e.forecast for e in base.forecasts] == [e.forecast for e in a.forecasts]
    rows = tuple(
        p.model_copy(
            update={"open": p.open * 2, "high": p.high * 2, "low": p.low * 2, "close": p.close * 2}
        )
        if p.session_date > d.observations[30].session_date
        else p
        for p in d.observations
    )
    b = evaluate(
        d.model_copy(update={"observations": rows}),
        s,
        executed_at=s.evaluation_cutoff,
        regime_analysis=True,
    )
    assert [e.regime for e in a.forecasts] == [e.regime for e in b.forecasts]
    assert [e.forecast for e in a.forecasts] == [e.forecast for e in b.forecasts]
    assert a.forecasts[0].metric_case.actual_price != b.forecasts[0].metric_case.actual_price
    small = classify(build_snapshot(d, request(d, index=30, lookback=20)))
    assert (
        small.trend == small.volatility == "UNAVAILABLE"
        and small.reason == "REGIME_REQUIRES_21_CONTEXT_CLOSES"
    )


def test_strict_conditional_synthetic_mode_quality_exclusions_not_promoted():
    *_, clock, cal, d = prepared()
    strict = evaluate(
        d, real_spec(d, clock[0], conditional=False), executed_at=clock[0], regime_analysis=True
    )
    conditional = evaluate(d, real_spec(d, clock[0]), executed_at=clock[0], regime_analysis=True)
    a = analysis(d, strict)
    b = analysis(d, conditional)
    assert all(c.samples.scored_origins == 0 and c.metrics.price_mae is None for c in a.cards)
    assert (
        all(c.samples.scored_origins == 3 for c in b.cards)
        and b.cards[0].evaluation_mode == "CONDITIONAL_HISTORICAL_REPLAY"
    )
    assert all(e.regime.latest_input_available_at > e.request.cutoff for e in conditional.forecasts)
    assert "DISJOINT_WINDOWS_DO_NOT_ESTABLISH_STATISTICAL_INDEPENDENCE" in b.warnings
    assert "REGIME_LABELS_SHARE_THE_EVALUATION_MODE_AVAILABILITY_AND_VINTAGE_LIMITS" in b.warnings


def test_aggregate_registry_is_bounded_expiring_and_excludes_per_origin_prices():
    from .forecast_research_fixtures import service_fixture

    s, reader, b, ref, clock, ticks, cal = service_fixture()
    body = b.model_copy(
        update={
            "start": cal.sessions[100].session_date,
            "end": cal.sessions[130].session_date,
            "regime_analysis": True,
        }
    )
    response = s.work("evaluate", reader, body, Event())
    reg = s.performance_registry()
    record = reg["records"][0]
    assert "performance" in response and set(record) == {
        "registry_id",
        "computed_at",
        "cards",
        "comparison",
    }
    assert "errors" not in record and "history" not in record and "regimes" not in record
    for n in range(33):
        ticks[0] += 61
        clock[0] += timedelta(seconds=1)
        s.work(
            "evaluate",
            reader,
            body.model_copy(
                update={
                    "rolling_error_window": 2 + n % 29,
                    "end": cal.sessions[100].session_date,
                    "lookback": 21,
                    "models": ["B01"],
                }
            ),
            Event(),
        )
    assert len(s.performance_registry()["records"]) == 32
    ticks[0] += 3601
    assert s.performance_registry()["records"] == []
    fresh = type(s)(s.market, calendar_override=cal)
    assert fresh.performance_registry()["records"] == []


def test_performance_cancellation_and_no_io(monkeypatch):
    import httpx
    import socket
    import sqlalchemy
    import builtins

    d, r = experiment()

    def forbidden(*a, **kw):
        raise AssertionError("UNAUTHORIZED_IO")

    monkeypatch.setattr(httpx.Client, "request", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(sqlalchemy, "create_engine", forbidden)
    monkeypatch.setattr(builtins, "open", forbidden)
    assert analysis(d, r).cards

    def cancel():
        raise ForecastError("FORECAST_CANCELLED")

    with pytest.raises(ForecastError, match="FORECAST_CANCELLED"):
        analysis(d, r, check=cancel)
