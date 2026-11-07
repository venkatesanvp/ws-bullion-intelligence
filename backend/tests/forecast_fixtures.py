"""Deliberately artificial calendar/prices; never evidence of NSE session dates."""

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo
from app.forecast_contracts import (
    Instrument,
    CalendarSession,
    TradingCalendar,
    ForecastObservation,
    ForecastDataset,
    Provenance,
    ForecastRequest,
)
from app.forecast_evaluation import EvaluationSpec, ForecastOrigin, ModelRun


def dataset(closes=None, count=40, future=150):
    closes = (
        tuple(Decimal(str(v)) for v in closes)
        if closes is not None
        else tuple(Decimal(100) + Decimal(i) / 10 for i in range(count))
    )
    sessions = []
    day = date(2024, 1, 1)
    zone = ZoneInfo("Asia/Kolkata")
    while len(sessions) < len(closes) + future:
        if day.weekday() < 5 and day not in {date(2024, 1, 4), date(2024, 1, 8)}:
            sessions.append(
                CalendarSession(
                    session_date=day, close_at=datetime.combine(day, time(15, 30), zone)
                )
            )
        day += timedelta(days=1)
    known = datetime(2023, 1, 1, tzinfo=timezone.utc)
    cal = TradingCalendar(
        calendar_id="SYNTHETIC_NOT_NSE",
        version="fixture-v1",
        timezone="Asia/Kolkata",
        known_at=known,
        coverage_start=sessions[0].session_date,
        coverage_end=sessions[-1].session_date,
        sessions=tuple(sessions),
    )
    rows = tuple(
        ForecastObservation(
            session_date=s.session_date,
            observed_at=s.close_at,
            available_at=s.close_at + timedelta(minutes=20),
            open=p,
            high=p,
            low=p,
            close=p,
            volume=1000,
            completed=True,
            quality="QUALIFIED_SYNTHETIC",
            provenance_ref="SYNTHETIC_ONLY",
        )
        for p, s in zip(closes, sessions)
    )
    return ForecastDataset(
        instrument=Instrument(
            instrument_id="TEST-SYNTH",
            symbol="SYNTH",
            exchange="SYNTHETIC_EXCHANGE",
            currency="INR",
        ),
        calendar=cal,
        provenance=Provenance(
            source_id="SYNTHETIC_GENERATOR",
            source_version="fixture-v1",
            dataset_label="SYNTHETIC_TEST_ONLY",
            evidence_ref="ARTIFICIAL_REFERENCE",
            known_at=known,
        ),
        basis="RAW_CLOSE",
        adjustment_policy_id="RAW_NO_ACTIONS",
        observations=rows,
    )


def request(data, model="B02", index=None, lookback=3, horizon=5, **kwargs):
    i = len(data.observations) - 1 if index is None else index
    s = data.calendar.sessions[i]
    return ForecastRequest(
        instrument=data.instrument,
        origin_session=s.session_date,
        horizon=horizon,
        lookback=lookback,
        model_id=model,
        cutoff=s.close_at + timedelta(hours=1),
        **kwargs,
    )


def spec(
    data,
    indices=(5, 10, 15),
    horizon=5,
    lookback=3,
    evaluation_index=30,
    models=("B01", "B02", "B03"),
    **kwargs,
):
    sessions = data.calendar.sessions
    return EvaluationSpec(
        horizon=horizon,
        lookback=lookback,
        origins=tuple(
            ForecastOrigin(
                session=sessions[i].session_date, cutoff=sessions[i].close_at + timedelta(hours=1)
            )
            for i in indices
        ),
        models=tuple(ModelRun(model_id=m) for m in models),
        evaluation_cutoff=sessions[evaluation_index].close_at + timedelta(hours=1),
        **kwargs,
    )
