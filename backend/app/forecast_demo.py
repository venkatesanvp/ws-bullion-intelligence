"""Explicit synthetic-only CLI: python -m app.forecast_demo. No external input or I/O."""

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
import json
from zoneinfo import ZoneInfo
from .forecast_contracts import (
    Instrument,
    CalendarSession,
    TradingCalendar,
    ForecastObservation,
    ForecastDataset,
    Provenance,
    Setting,
)
from .forecast_evaluation import EvaluationSpec, ForecastOrigin, ModelRun, evaluate


def synthetic_example():
    zone = ZoneInfo("Asia/Kolkata")
    sessions, day = [], date(2020, 1, 1)
    artificial_holidays = {date(2020, 1, 4), date(2020, 1, 8)}
    while len(sessions) < 950:
        if day.weekday() < 5 and day not in artificial_holidays:
            sessions.append(
                CalendarSession(
                    session_date=day, close_at=datetime.combine(day, time(15, 30), zone)
                )
            )
        day += timedelta(days=1)
    known = datetime(2019, 1, 1, tzinfo=timezone.utc)
    calendar = TradingCalendar(
        calendar_id="SYNTHETIC_NOT_NSE",
        version="artificial-calendar-v1",
        timezone="Asia/Kolkata",
        known_at=known,
        coverage_start=sessions[0].session_date,
        coverage_end=sessions[-1].session_date,
        sessions=tuple(sessions),
    )
    rows = []
    for i, s in enumerate(sessions[:800]):
        price = Decimal(100) + Decimal(i) / 100 + Decimal(i % 7 - 3) / 5
        rows.append(
            ForecastObservation(
                session_date=s.session_date,
                observed_at=s.close_at,
                available_at=s.close_at + timedelta(minutes=20),
                open=price,
                high=price,
                low=price,
                close=price,
                volume=1000,
                completed=True,
                quality="QUALIFIED_SYNTHETIC",
                provenance_ref="SYNTHETIC_FORMULA_V1",
            )
        )
    dataset = ForecastDataset(
        instrument=Instrument(
            instrument_id="SYNTHETIC-INSTRUMENT",
            symbol="SYNTH",
            exchange="SYNTHETIC_EXCHANGE",
            currency="INR",
        ),
        calendar=calendar,
        provenance=Provenance(
            source_id="SYNTHETIC_GENERATOR",
            source_version="v1",
            dataset_label="SYNTHETIC_NOT_MARKET_DATA",
            evidence_ref="DETERMINISTIC_FORMULA_ONLY",
            known_at=known,
        ),
        basis="RAW_CLOSE",
        adjustment_policy_id="RAW_NO_ACTIONS",
        observations=tuple(rows),
    )
    cutoff = sessions[799].close_at + timedelta(hours=1)
    spec = EvaluationSpec(
        horizon=5,
        lookback=253,
        origins=tuple(
            ForecastOrigin(
                session=sessions[i].session_date, cutoff=sessions[i].close_at + timedelta(hours=1)
            )
            for i in range(500, 600, 5)
        ),
        models=(
            ModelRun(model_id="B01"),
            ModelRun(model_id="B02"),
            ModelRun(
                model_id="B03", configuration=(Setting(name="annualization_sessions", value=252),)
            ),
        ),
        evaluation_cutoff=cutoff,
        overlap_policy="REQUIRE_NONOVERLAPPING",
    )
    return dataset, spec


def main():
    dataset, spec = synthetic_example()
    result = evaluate(dataset, spec, executed_at=datetime.now(timezone.utc))
    summary = {
        "classification": result.classification,
        "retention": result.retention,
        "experiment_id": result.experiment_id,
        "dataset_fingerprint": result.dataset_fingerprint,
        "executed_at": result.executed_at.isoformat(),
        "forecast_count": len(result.forecasts),
        "exclusion_count": len(result.exclusions),
        "matured_unique_origins": result.matured_unique_origins,
        "max_disjoint_windows": result.max_disjoint_matured_windows,
        "warnings": result.warnings,
        "evaluations": [e.model_dump(mode="json") for e in result.evaluations],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
