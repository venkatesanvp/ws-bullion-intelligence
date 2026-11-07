"""Fixed descriptive rules on the already-qualified origin snapshot only."""

from decimal import Decimal, DecimalException
from .forecast_contracts import ForecastError
from .forecast_baselines import context, derived, simple_returns, sample_sigma
from .forecast_performance_contracts import RegimeEvidence

VERSION = "fixed-21-close-v1"


def classify(snapshot):
    rows = snapshot.observations[-21:]
    base = dict(
        origin=snapshot.origin_session,
        first_session=rows[0].session_date if len(rows) == 21 else None,
        input_count=len(rows),
        context_fingerprint=snapshot.fingerprint,
        latest_input_available_at=max(r.available_at for r in rows),
    )
    if len(rows) < 21:
        return RegimeEvidence(
            **base,
            trend="UNAVAILABLE",
            volatility="UNAVAILABLE",
            efficiency=None,
            trailing_return=None,
            session_sigma=None,
            reason="REGIME_REQUIRES_21_CONTEXT_CLOSES",
        )
    try:
        with context():
            cs = tuple(r.close for r in rows)
            changes = tuple(b - a for a, b in zip(cs, cs[1:]))
            distance = sum((abs(x) for x in changes), Decimal(0))
            efficiency = abs(cs[-1] - cs[0]) / distance if distance else Decimal(0)
            change = cs[-1] / cs[0] - 1
            sigma = sample_sigma(simple_returns(cs))
            return RegimeEvidence(
                **base,
                trend="TRENDING"
                if efficiency >= Decimal(".35") and abs(change) >= Decimal(".02")
                else "SIDEWAYS",
                volatility="HIGH" if sigma >= Decimal(".015") else "LOW",
                efficiency=derived(efficiency),
                trailing_return=derived(change),
                session_sigma=derived(sigma),
                reason=None,
            )
    except (DecimalException, ForecastError):
        return RegimeEvidence(
            **base,
            trend="UNAVAILABLE",
            volatility="UNAVAILABLE",
            efficiency=None,
            trailing_return=None,
            session_sigma=None,
            reason="REGIME_NUMERIC_UNSUPPORTED",
        )
