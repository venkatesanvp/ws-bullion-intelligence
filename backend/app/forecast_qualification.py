"""Structural/evidential qualification summaries; no source promotion or I/O."""

from datetime import date
from .forecast_contracts import ForecastError
from .forecast_market_contracts import MarketDataset
from .forecast_replay import ASSUMPTIONS, POLICY


def qualification(dataset, metadata, profile):
    real = isinstance(dataset, MarketDataset)
    raw = profile.get("known_break_dates", [])
    if not isinstance(raw, list) or len(raw) > 500:
        raise ForecastError("INVALID_DECLARED_BREAK_METADATA")
    try:
        breaks = tuple(sorted(set(date.fromisoformat(x) for x in raw)))
    except (ValueError, TypeError):
        raise ForecastError("INVALID_DECLARED_BREAK_METADATA") from None
    rows = dataset.observations
    report = {
        "status": "STRUCTURAL_ONLY_CONDITIONAL_REPLAY_NOT_FULL_SOURCE_QUALIFICATION"
        if real
        else "SYNTHETIC_TEST_ONLY",
        "observation_timestamps": {
            "original_event_present": sum(r.source_event_at is not None for r in rows)
            if real
            else len(rows),
            "policy": "ORIGINAL_NULLS_PRESERVED_SESSION_CLOSE_IS_SEPARATE_PROXY",
        },
        "availability": {
            "local_first_seen_present": len(rows),
            "historical_provider_publication": "UNVERIFIED" if real else "SYNTHETIC_DECLARED",
        },
        "finality": "PRIOR_DATE_COMPLETED_DAILY_CANDIDATE_NOT_INDEPENDENTLY_CERTIFIED"
        if real
        else "SYNTHETIC_DECLARED",
        "calendar": {
            "version": dataset.calendar.version,
            "coverage_start": str(dataset.calendar.coverage_start),
            "coverage_end": str(dataset.calendar.coverage_end),
            "reviewed_at": dataset.calendar.known_at.isoformat(),
            "missing_sessions": metadata["missing_sessions"],
        },
        "adjustments": {
            "basis": dataset.basis,
            "methodology": "UNQUALIFIED" if real else "SYNTHETIC_DECLARED",
            "declared_breaks": [str(x) for x in breaks],
            "unknown_actions": "NOT_RULED_OUT" if real else "SYNTHETIC_DECLARED",
        },
        "revisions": "AS_RETRIEVED_SNAPSHOT_NO_HISTORICAL_VINTAGE_ARCHIVE"
        if real
        else "SYNTHETIC_DECLARED",
        "provenance": "CANONICAL_ID_HASH_BATCH_AND_ORIGINAL_TIMES_PRESERVED",
        "rights": "EXISTING_OWNER_TRANSIENT_PRIVATE_ANALYSIS_DISPLAY_ONLY_NO_PERSISTENCE_OR_REDISTRIBUTION"
        if real
        else "SYNTHETIC_TEST_ONLY",
        "modes": ["STRICT_POINT_IN_TIME", "CONDITIONAL_HISTORICAL_REPLAY"]
        if real
        else ["SYNTHETIC"],
        "conditional_policy": POLICY if real else None,
        "conditional_assumptions": list(ASSUMPTIONS) if real else [],
    }
    return report, breaks
