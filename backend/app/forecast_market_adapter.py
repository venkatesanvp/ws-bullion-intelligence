"""Read-only canonical-to-forecast adaptation. No provider retrieval or persistence."""

from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
import json
from zoneinfo import ZoneInfo
from pydantic import ValidationError
from .forecast_contracts import (
    Instrument,
    CalendarSession,
    TradingCalendar,
    Provenance,
    ForecastObservation,
    ForecastDataset,
    ForecastError,
    fingerprint,
    utc,
)
from .forecast_market_contracts import MarketProvenance, MarketObservation, MarketDataset

IST = ZoneInfo("Asia/Kolkata")
LIMITATIONS = (
    "TRANSIENT_OWNER_RESEARCH_NOT_FULL_SOURCE_QUALIFICATION",
    "LOCAL_FIRST_SEEN_IS_NOT_HISTORICAL_PUBLICATION",
    "PROVIDER_TIMESTAMP_SEMANTICS_UNQUALIFIED",
    "PROVIDER_ADJUSTMENT_AND_TOTAL_RETURN_UNQUALIFIED",
    "SESSION_CLOSE_IS_A_CALENDAR_PROXY_NOT_PROVIDER_EVENT_TIME",
    "NO_CALIBRATED_PROBABILITIES_OR_RELIABILITY_CLAIM",
)


@dataclass(frozen=True)
class Adapted:
    dataset: ForecastDataset
    metadata: dict
    references: tuple
    unknown_target_times: frozenset


def chart_history(observations):
    """Exact display-only metadata from the same eligible model observations."""
    return [
        {"time": str(p.session_date), "open": format(p.open, "f"),
         "high": format(p.high, "f"), "low": format(p.low, "f"),
         "close": format(p.close, "f"), "volume": str(p.volume)}
        for p in observations
    ]


def calendar_view(profile, override=None):
    if override is not None:
        return override, frozenset()
    if not profile:
        raise ForecastError("CALENDAR_UNAVAILABLE")
    extra = json.loads(
        Path(__file__).with_name("forecast_calendar_extension.json").read_text(encoding="utf-8")
    )
    start, end = (
        date.fromisoformat(profile["coverage_start"]),
        date.fromisoformat(profile["coverage_end"]),
    )
    days = set(date.fromisoformat(d) if isinstance(d, str) else d for d in profile["session_dates"])
    extension_start = date.fromisoformat(extra["coverage_start"])
    if end.toordinal() + 1 == extension_start.toordinal():
        days.update(date.fromisoformat(d) for d in extra["session_dates"])
        end = date.fromisoformat(extra["coverage_end"])
    unknown = frozenset(date.fromisoformat(d) for d in extra["unknown_close_sessions"])
    sessions = tuple(
        CalendarSession(
            session_date=d,
            close_at=datetime.combine(d, time(23, 59, 59) if d in unknown else time(15, 30), IST),
        )
        for d in sorted(days)
    )
    cal = TradingCalendar(
        calendar_id="NSE_CM_FORECAST_REVIEW",
        version=profile["version"] + "+" + extra["version"],
        timezone="Asia/Kolkata",
        known_at=datetime.fromisoformat(extra["reviewed_at"]),
        coverage_start=start,
        coverage_end=end,
        sessions=sessions,
    )
    return cal, unknown


def adapt(instrument, source, rows, *, listings, now, calendar_override=None):
    now = utc(now)
    listing = next((x for x in listings if x.isin == instrument.isin), None)
    if listing is None or any(
        getattr(listing, k) != getattr(instrument, k) for k in ("symbol", "exchange", "currency")
    ):
        raise ForecastError("UNSUPPORTED_OR_MISMATCHED_INSTRUMENT")
    permitted = source.permitted_uses or {}
    if (
        source.source_kind != "DHANHQ"
        or source.qualification
        not in {"TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED", "QUALIFIED_FOR_RESEARCH"}
        or not all(permitted.get(k) is True for k in ("retrieval", "analysis", "display"))
    ):
        raise ForecastError("SOURCE_RESEARCH_USE_NOT_AUTHORIZED")
    real = source.profile.get("data_class") == "REAL_MARKET"
    if not real and source.profile.get("data_class") != "SYNTHETIC_TEST":
        raise ForecastError("SOURCE_DATA_CLASS_UNAVAILABLE")
    if len(rows) > 5000:
        raise ForecastError("FORECAST_INPUT_LIMIT")
    dates = [r.trading_date for r in rows]
    if dates != sorted(set(dates)):
        raise ForecastError("DUPLICATE_OR_UNORDERED_CANONICAL_SESSION")
    if any(r.price_basis != "PROVIDER_ADJUSTED" for r in rows):
        raise ForecastError("MIXED_CANONICAL_PRICE_BASIS")
    try:
        event_times = [utc(r.event_time) for r in rows if r.event_time is not None]
    except (ValueError, AttributeError):
        raise ForecastError("INVALID_CANONICAL_EVENT_TIMESTAMP") from None
    if len(event_times) != len(set(event_times)):
        raise ForecastError("DUPLICATE_PROVIDER_EVENT_TIMESTAMP")
    try:
        cal, unknown = calendar_view(source.profile.get("calendar"), calendar_override)
    except ForecastError:
        raise
    except (KeyError, TypeError, ValueError):
        raise ForecastError("INVALID_OR_UNQUALIFIED_CALENDAR") from None
    sessions = {s.session_date: s for s in cal.sessions}
    selected = []
    refs = []
    excluded = {
        "outside_calendar": 0,
        "not_final_daily": 0,
        "missing_first_seen": 0,
        "unavailable_at_cutoff": 0,
    }
    for r in rows:
        if r.interval != "1d" or r.trading_date >= now.astimezone(IST).date():
            excluded["not_final_daily"] += 1
            continue
        if r.trading_date not in sessions:
            excluded["outside_calendar"] += 1
            continue
        if r.ingested_at is None:
            excluded["missing_first_seen"] += 1
            continue
        try:
            seen = utc(r.ingested_at)
        except (ValueError, AttributeError):
            raise ForecastError("INVALID_FIRST_SEEN_TIMESTAMP") from None
        if seen > now:
            excluded["unavailable_at_cutoff"] += 1
            continue
        try:
            if (r.event_time is not None and utc(r.event_time) > seen) or (
                r.provider_published_at is not None and utc(r.provider_published_at) > seen
            ):
                raise ForecastError("CANONICAL_TIMESTAMP_AFTER_FIRST_SEEN")
        except (ValueError, AttributeError) as err:
            if isinstance(err, ForecastError):
                raise
            raise ForecastError("INVALID_CANONICAL_TEMPORAL_METADATA") from None
        s = sessions[r.trading_date]
        if seen < s.close_at:
            raise ForecastError("FIRST_SEEN_BEFORE_FINAL_SESSION_COMPLETION")
        common = dict(
            session_date=r.trading_date,
            observed_at=s.close_at,
            available_at=seen,
            open=r.open,
            high=r.high,
            low=r.low,
            close=r.close,
            volume=r.volume,
            completed=True,
            quality="CONDITIONAL_OWNER_RESEARCH" if real else "QUALIFIED_SYNTHETIC",
            provenance_ref=str(r.batch_id),
        )
        try:
            if real:
                point = MarketObservation(
                    **common,
                    source_event_precision=r.event_precision,
                    source_event_at=r.event_time,
                    provider_published_at=r.provider_published_at,
                    canonical_id=str(r.id),
                    canonical_hash=r.canonical_hash,
                    batch_id=str(r.batch_id),
                    source_row=r.row_number,
                    session_time_policy="EXCHANGE_SESSION_CLOSE_PROXY_NOT_PROVIDER_TIMESTAMP",
                    finality="PRIOR_DATE_DAILY_COMPLETED_CANDIDATE",
                )
            else:
                point = ForecastObservation(**common)
        except (ValidationError, ValueError):
            raise ForecastError("INVALID_CANONICAL_FORECAST_OBSERVATION") from None
        selected.append(point)
        refs.append((r.trading_date, str(r.id), r.canonical_hash))
    identity = Instrument(
        instrument_id=str(instrument.id),
        symbol=instrument.symbol,
        exchange=instrument.exchange,
        currency=instrument.currency,
        isin=instrument.isin,
    )
    known = utc(source.reviewed_at) if source.reviewed_at else now
    provenance = dict(
        source_id=str(source.id),
        source_version=source.contract_version,
        dataset_label=source.label[:128],
        evidence_ref=(source.rights_evidence_ref or "NO_EVIDENCE")[:128],
        known_at=known,
    )
    try:
        if real:
            prov = MarketProvenance(
                **provenance,
                data_class="REAL_MARKET",
                availability_policy="LOCAL_FIRST_SEEN_ONLY",
                permission_scope="TRANSIENT_OWNER_RESEARCH_ONLY",
                source_qualification=source.qualification,
                source_profile_fingerprint=fingerprint(source.profile),
                adjustment_reference=source.profile.get("adjustment_definition_ref"),
                timestamp_policy_reference=(source.profile.get("acquisition_review") or {}).get(
                    "timestamp_policy"
                ),
                limitations=LIMITATIONS,
            )
            data = MarketDataset(
                instrument=identity,
                calendar=cal,
                provenance=prov,
                basis="PROVIDER_ADJUSTED_UNVERIFIED",
                adjustment_policy_id="PROVIDER_AS_DELIVERED_ADJUSTMENT_UNQUALIFIED",
                observations=tuple(selected),
            )
        else:
            data = ForecastDataset(
                instrument=identity,
                calendar=cal,
                provenance=Provenance(**provenance),
                basis="RAW_CLOSE",
                adjustment_policy_id="RAW_NO_ACTIONS",
                observations=tuple(selected),
            )
    except (ValidationError, ValueError):
        raise ForecastError("INVALID_FORECAST_DATASET_METADATA") from None
    actual_gaps = []
    if selected:
        present = {r.session_date for r in selected}
        actual_gaps = [
            s.session_date
            for s in cal.sessions
            if selected[0].session_date <= s.session_date <= selected[-1].session_date
            and s.session_date not in present
        ]
    last = selected[-1] if selected else None
    metadata = {
        "instrument": identity.model_dump(mode="json"),
        "source_id": str(source.id),
        "source": source.label,
        "source_qualification": source.qualification,
        "data_class": "REAL_MARKET" if real else "SYNTHETIC_TEST",
        "quality": "CONDITIONAL_OWNER_RESEARCH" if real else "QUALIFIED_SYNTHETIC",
        "canonical_basis": "PROVIDER_ADJUSTED",
        "model_basis": data.basis,
        "available_first_date": str(rows[0].trading_date) if rows else None,
        "available_last_date": str(rows[-1].trading_date) if rows else None,
        "available_observations": len(rows),
        "eligible_observations": len(selected),
        "excluded_observations": excluded,
        "missing_sessions": len(actual_gaps),
        "first_date": str(selected[0].session_date) if selected else None,
        "last_date": str(last.session_date) if last else None,
        "last_close": format(last.close, "f") if last else None,
        "last_first_seen_at": last.available_at.isoformat() if last else None,
        "last_source_event_at": r.event_time.isoformat()
        if last and (r := next(x for x in rows if x.trading_date == last.session_date)).event_time
        else None,
        "calendar_version": cal.version,
        "calendar_coverage_end": str(cal.coverage_end),
        "calendar_known_at": cal.known_at.isoformat(),
        "freshness": "NO_FINAL_DAILY_DATA"
        if not last
        else "LATEST_PRIOR_DATE_DAILY_CANDIDATE"
        if len(
            [s for s in cal.sessions if last.session_date < s.session_date and s.close_at <= now]
        )
        <= 1
        else "STALE_FINAL_DAILY_INPUT",
        "limitations": list(LIMITATIONS) if real else ["SYNTHETIC_TEST_ONLY"],
        "history": chart_history(selected[-120:]),
        "retention": "PROCESS_MEMORY_ONLY_RESTART_LOSES_TRACKING",
    }
    return Adapted(data, metadata, tuple(refs), unknown)
