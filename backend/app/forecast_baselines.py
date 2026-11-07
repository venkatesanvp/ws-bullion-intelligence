"""Deterministic B01/B02/B03. Models consume snapshots only, never full datasets."""

from datetime import datetime
from decimal import Context, Decimal, DecimalException, ROUND_HALF_EVEN, Underflow, localcontext
from pydantic import ValidationError
from .forecast_market_contracts import MarketSnapshot, MarketRequest, MarketResult, MarketDescriptor
from .forecast_contracts import (
    ForecastRequest,
    ForecastSnapshot,
    ForecastResult,
    ModelDescriptor,
    ForecastError,
    NUMERIC_VERSION,
    fingerprint,
    utc,
)

from .forecast_replay import ReplaySnapshot, ReplayRequest, ReplayResult, ASSUMPTIONS

VERSION = "baseline-simple-v1"
SCALE = Decimal("0.000000000001")


def context():
    ctx = Context(prec=34, rounding=ROUND_HALF_EVEN, Emax=96, Emin=-96)
    ctx.traps[Underflow] = True
    return localcontext(ctx)


def derived(value):
    if not value.is_finite():
        raise ForecastError("NUMERIC_UNSUPPORTED")
    try:
        value = value.quantize(SCALE)
    except DecimalException:
        raise ForecastError("NUMERIC_UNSUPPORTED") from None
    return abs(value) if value.is_zero() else value


def simple_returns(closes):
    return tuple(b / a - 1 for a, b in zip(closes, closes[1:]))


def sample_sigma(returns):
    if len(returns) < 2:
        raise ForecastError("INSUFFICIENT_MODEL_HISTORY")
    mean = sum(returns, Decimal(0)) / len(returns)
    variance = sum(((r - mean) ** 2 for r in returns), Decimal(0)) / (len(returns) - 1)
    return variance.sqrt()


def baseline_configuration(request):
    config = {s.name: s.value for s in request.configuration}
    if set(config) - {"return_convention", "annualization_sessions"}:
        raise ForecastError("UNSUPPORTED_MODEL_CONFIGURATION")
    if config.get("return_convention", "SIMPLE") != "SIMPLE":
        raise ForecastError("UNSUPPORTED_RETURN_CONVENTION")
    annualization = config.get("annualization_sessions")
    if annualization is not None and (
        request.model_id != "B03"
        or type(annualization) is not int
        or not 1 <= annualization <= 1000
    ):
        raise ForecastError("INVALID_ANNUALIZATION")
    return annualization


DESCRIPTORS = (
    ModelDescriptor(
        model_id="B01", version=VERSION, min_closes=1, capabilities=("POINT_PRICE", "POINT_RETURN")
    ),
    ModelDescriptor(
        model_id="B02", version=VERSION, min_closes=2, capabilities=("POINT_PRICE", "POINT_RETURN")
    ),
    ModelDescriptor(model_id="B03", version=VERSION, min_closes=3, capabilities=("VOLATILITY",)),
)


class BaselineModel:
    def __init__(self, descriptor):
        self.descriptor = descriptor

    def predict(
        self, snapshot: ForecastSnapshot, request: ForecastRequest, *, created_at: datetime
    ) -> ForecastResult:
        try:
            replay = type(snapshot) is ReplaySnapshot
            real = type(snapshot) is MarketSnapshot or replay
            snapshot = (
                ReplaySnapshot if replay else MarketSnapshot if real else ForecastSnapshot
            ).model_validate(snapshot.model_dump())
            request = (
                ReplayRequest if replay else MarketRequest if real else ForecastRequest
            ).model_validate(request.model_dump())
            created_at = utc(created_at)
        except (ValidationError, ValueError, AttributeError):
            raise ForecastError("INVALID_SNAPSHOT_OR_REQUEST") from None
        if request.model_id != self.descriptor.model_id or any(
            getattr(request, k) != getattr(snapshot, k)
            for k in (
                "instrument",
                "timeframe",
                "origin_session",
                "horizon",
                "lookback",
                "cutoff",
                "quality",
            )
        ):
            raise ForecastError("SNAPSHOT_REQUEST_MISMATCH")
        if replay and (
            created_at < request.assessment_cutoff
            or request.assessment_cutoff != snapshot.assessment_cutoff
            or request.assumption_policy != snapshot.assumption_policy
        ):
            raise ForecastError("REPLAY_ASSESSMENT_MISMATCH")
        if created_at < request.cutoff:
            raise ForecastError("EXECUTION_BEFORE_CUTOFF")
        if len(snapshot.observations) < self.descriptor.min_closes:
            raise ForecastError("INSUFFICIENT_MODEL_HISTORY")
        annualization = baseline_configuration(request)
        warnings = [
            "CONDITIONAL_REAL_RESEARCH_NOT_SOURCE_QUALIFICATION"
            if real
            else "SYNTHETIC_ONLY_NO_REAL_MARKET_ACCURACY",
            "NO_CALIBRATED_PROBABILITIES",
            "NO_VALIDATED_FORWARD_PERFORMANCE_CLAIM"
            if real
            else "HISTORICAL_REPLAY_NOT_FORWARD_EVIDENCE",
        ]
        if request.model_id != "B01" and request.lookback < 253:
            warnings.append("BELOW_PROPOSED_RESEARCH_SUPPORT_FLOOR")
        values = {}
        try:
            with context():
                closes = tuple(r.close for r in snapshot.observations)
                last = closes[-1]
                if request.model_id == "B01":
                    values = {"predicted_price": last, "predicted_return": derived(Decimal(0))}
                elif request.model_id == "B02":
                    returns = simple_returns(closes)
                    mean = sum(returns, Decimal(0)) / len(returns)
                    factor = (1 + mean) ** request.horizon
                    values = {
                        "predicted_price": derived(last * factor),
                        "predicted_return": derived(factor - 1),
                    }
                else:
                    sigma = sample_sigma(simple_returns(closes))
                    values = {
                        "session_volatility": derived(sigma),
                        "horizon_volatility": derived(sigma * Decimal(request.horizon).sqrt()),
                        "annualized_volatility": derived(sigma * Decimal(annualization).sqrt())
                        if annualization
                        else None,
                    }
                    warnings.append("IID_SQRT_SESSION_SCALING_ASSUMPTION")
        except DecimalException:
            raise ForecastError("NUMERIC_UNSUPPORTED") from None
        if values.get("predicted_price") is not None and values["predicted_price"] <= 0:
            raise ForecastError("NUMERIC_UNSUPPORTED")
        unsupported = (
            "prediction_intervals",
            "probability_positive",
            "calibration",
            "scenario_paths",
        ) + (
            ("predicted_price", "predicted_return")
            if request.model_id == "B03"
            else ("session_volatility", "horizon_volatility", "annualized_volatility")
        )
        descriptor = (
            MarketDescriptor.model_validate(
                {
                    **self.descriptor.model_dump(),
                    "lifecycle": "TRANSIENT_CONDITIONAL_REAL_RESEARCH_ONLY",
                }
            )
            if real
            else self.descriptor
        )
        forecast_id = fingerprint(
            {
                "snapshot": snapshot.fingerprint,
                "request": request,
                "model": descriptor,
                "numeric": NUMERIC_VERSION,
            }
        )
        result_type = ReplayResult if replay else MarketResult if real else ForecastResult
        if replay:
            warnings.extend(ASSUMPTIONS)
        if real:
            warnings.extend(snapshot.provenance.limitations)
        return result_type(
            observations_validated=snapshot.lookback,
            effective_closes_used=1 if request.model_id == "B01" else snapshot.lookback,
            return_observations_used=0 if request.model_id == "B01" else snapshot.lookback - 1,
            last_observed_close=snapshot.observations[-1].close,
            last_observation_at=snapshot.observations[-1].source_event_at
            if real
            else snapshot.observations[-1].observed_at,
            last_availability_at=snapshot.observations[-1].available_at,
            last_session_close_proxy=snapshot.context_sessions[-1].close_at,
            forecast_id=forecast_id,
            model=descriptor,
            instrument=request.instrument,
            horizon=request.horizon,
            origin_session=request.origin_session,
            target_session=snapshot.target_session.session_date,
            created_at=created_at,
            cutoff=request.cutoff,
            dataset_fingerprint=snapshot.fingerprint,
            configuration=request.configuration,
            basis=snapshot.basis,
            provenance=snapshot.provenance,
            unsupported_fields=unsupported,
            warnings=tuple(warnings),
            **(
                {
                    "assumption_policy": request.assumption_policy,
                    "assessment_cutoff": request.assessment_cutoff,
                }
                if replay
                else {}
            ),
            **values,
        )


def get_model(model_id):
    descriptor = next((d for d in DESCRIPTORS if d.model_id == model_id), None)
    if descriptor is None:
        raise ForecastError("MODEL_NOT_REGISTERED")
    return BaselineModel(descriptor)
