from datetime import date, datetime, timezone
from uuid import UUID
from sqlalchemy import func, select
from .errors import APIError
from .models import DataSource, ImportBatch, Instrument, Observation, QualityResult
from .serialization import digest, plain


def find(db, model, value):
    result = db.get(model, value)
    if result is None:
        raise APIError(404, "NOT_FOUND", "The requested record does not exist.")
    return result


def series(db, instrument_id: UUID, source_id: UUID):
    instrument = find(db, Instrument, instrument_id)
    source = find(db, DataSource, source_id)
    if source.qualification != "QUALIFIED_FOR_RESEARCH":
        raise APIError(
            403, "SOURCE_NOT_QUALIFIED", "This source is not qualified for research display."
        )
    return instrument, source


def series_meta(
    db,
    instrument: Instrument,
    source: DataSource,
    basis: str,
    start: date | None,
    end: date | None,
    as_of: datetime | None = None,
):
    conditions = [
        Observation.instrument_id == instrument.id,
        Observation.source_id == source.id,
        Observation.price_basis == basis,
        Observation.interval == "1d",
    ]
    first, last, total = db.execute(
        select(
            func.min(Observation.trading_date), func.max(Observation.trading_date), func.count()
        ).where(*conditions)
    ).one()
    selected_conditions = list(conditions)
    if start:
        selected_conditions.append(Observation.trading_date >= start)
    if end:
        selected_conditions.append(Observation.trading_date <= end)
    range_first, range_last, count = db.execute(
        select(
            func.min(Observation.trading_date), func.max(Observation.trading_date), func.count()
        ).where(*selected_conditions)
    ).one()
    assessment = as_of or datetime.now(timezone.utc)
    if assessment.tzinfo is None or assessment.utcoffset() is None:
        raise APIError(422, "TIMEZONE_REQUIRED", "Assessment time requires a timezone.")
    profile = source.profile
    calendar = profile.get("calendar")
    missing = []
    continuity = "UNVERIFIED"
    if calendar and count:
        window_start, window_end = start or range_first, end or range_last
        lower = max(window_start.isoformat(), calendar["coverage_start"])
        upper = min(window_end.isoformat(), calendar["coverage_end"])
        expected = {date.fromisoformat(d) for d in calendar["session_dates"] if lower <= d <= upper}
        observed = (
            set(
                db.scalars(
                    select(Observation.trading_date).where(
                        *selected_conditions,
                        Observation.trading_date >= date.fromisoformat(lower),
                        Observation.trading_date <= date.fromisoformat(upper),
                    )
                )
            )
            if lower <= upper
            else set()
        )
        missing = sorted(expected - observed)
        fully_covered = (
            calendar["coverage_start"] <= window_start.isoformat()
            and window_end.isoformat() <= calendar["coverage_end"]
        )
        continuity = (
            ("ASSESSED_WITH_GAPS" if missing else "ASSESSED_WITHIN_CALENDAR_COVERAGE")
            if fully_covered
            else "PARTIALLY_ASSESSED"
        )
    publication_unknown = (
        db.scalar(
            select(func.count())
            .select_from(Observation)
            .where(*conditions, Observation.provider_published_at.is_(None))
        )
        or 0
    )
    freshness = {
        "status": "UNASSESSED",
        "assessment_as_of": plain(assessment),
        "expected_latest_date": None,
        "actual_latest_date": plain(last) if last else None,
        "policy_version": profile["policy_version"],
        "reason": "NO_APPLICABLE_APPROVED_AS_OF_POLICY",
    }
    policy = profile.get("freshness")
    if (
        policy
        and datetime.fromisoformat(policy["assessment_as_of"].replace("Z", "+00:00")) == assessment
    ):
        expected_latest = date.fromisoformat(policy["expected_latest_session"])
        freshness.update(expected_latest_date=plain(expected_latest))
        if last and last <= expected_latest:
            freshness.update(
                status="FRESH" if last == expected_latest else "STALE",
                reason="EXPLICIT_SOURCE_AS_OF_POLICY",
            )
    issue_counts = dict(
        db.execute(
            select(QualityResult.severity, func.count())
            .join(ImportBatch, ImportBatch.id == QualityResult.batch_id)
            .where(ImportBatch.instrument_id == instrument.id, ImportBatch.source_id == source.id)
            .group_by(QualityResult.severity)
        ).all()
    )
    flags = []
    if not calendar:
        flags.append("CALENDAR_UNVERIFIED")
    if publication_unknown:
        flags.append("PUBLICATION_TIME_UNKNOWN")
    if not profile.get("adjustment_definition_ref"):
        flags.append("CORPORATE_ACTIONS_UNASSESSED")
    if basis == "UNKNOWN":
        flags.append("BASIS_UNVERIFIED")
    if missing:
        flags.append("MISSING_SESSIONS")
    return {
        "series_ref": {
            "instrument_id": str(instrument.id),
            "source_id": str(source.id),
            "interval": "1d",
            "price_basis": basis,
            "revision": instrument.data_revision,
            "profile_digest": digest(profile),
        },
        "source": {
            "id": str(source.id),
            "label": source.label,
            "data_class": profile["data_class"],
            "qualification": source.qualification,
            "verification": "OWNER_RECORDED_NOT_THIRD_PARTY_VERIFIED",
        },
        "coverage": {
            "count": count,
            "dataset_count": total,
            "dataset_first_date": plain(first) if first else None,
            "dataset_last_date": plain(last) if last else None,
            "range_first_date": plain(range_first) if range_first else None,
            "range_last_date": plain(range_last) if range_last else None,
        },
        "quality": {
            "flags": flags,
            "continuity": continuity,
            "missing_session_count": len(missing),
            "missing_session_dates": plain(missing[:100]),
            "import_issue_counts": issue_counts,
            "publication_unknown_count": publication_unknown,
            "known_break_dates": [
                d
                for d in profile.get("known_break_dates", [])
                if (start is None or d >= start.isoformat())
                and (end is None or d <= end.isoformat())
            ],
        },
        "freshness": freshness,
        "limitations": [
            "DESCRIPTIVE_HISTORY_ONLY",
            "UNVERIFIED_FOR_REPLAY",
            "NO_INFERRED_PUBLICATION_TIME",
            "NOT_LIVE_OR_EXECUTABLE_PRICES",
        ],
    }
