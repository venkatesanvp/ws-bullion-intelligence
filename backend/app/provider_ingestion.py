"""Provider candidates -> existing atomic ingestion repository. No network operations."""

from decimal import Decimal
from datetime import datetime
from uuid import UUID

from .acquisition import CollectedSeries
from .daily_values import price
from .dhan_history_contract import MIN_CANDIDATE_SECONDS, MAX_CANDIDATE_SECONDS, _candidate_nse_date
from .errors import APIError
from .ingestion import Report, _ingest
from .schemas import CanonicalImportMetadata
from .serialization import digest, plain


def validate_source_policy(source, *, reference=None):
    uses = source.permitted_uses
    review = source.profile.get("acquisition_review") or {}
    if (
        source.source_kind != "DHANHQ"
        or source.contract_version != "dhan-daily-v1-provisional"
        or source.qualification != "QUALIFIED_FOR_RESEARCH"
        or not source.rights_evidence_ref
        or not source.reviewed_at
        or not all(uses.get(k) for k in ("retrieval", "storage", "analysis", "display"))
        or not uses.get("retention_review_ref")
    ):
        raise APIError(
            403,
            "SOURCE_NOT_QUALIFIED",
            "Record applicable data-use and retention evidence before persistence.",
        )
    if reference is not None and source.rights_evidence_ref != reference:
        raise APIError(409, "SOURCE_PROFILE_CHANGED", "Refresh the reviewed source profile.")
    if (
        review.get("timestamp_policy") != "UNIX_SECONDS_IST_CANDIDATE_V1"
        or review.get("allow_provisional_session_dates") is not True
        or not review.get("review_ref")
    ):
        raise APIError(
            403,
            "TIMESTAMP_POLICY_NOT_REVIEWED",
            "Review the provisional session-mapping policy before persistence.",
        )


def ingest_collected(
    db,
    collected: CollectedSeries,
    meta: CanonicalImportMetadata,
    request_key: UUID,
    request_id: str,
    *,
    persistence_approved: bool = False,
):
    if persistence_approved is not True:
        raise APIError(
            403, "PERSISTENCE_APPROVAL_REQUIRED", "Explicit persistence approval is required."
        )
    if (
        collected.plan_fingerprint != meta.plan_fingerprint
        or collected.requested_start != meta.requested_start
        or collected.requested_end != meta.requested_end
    ):
        raise APIError(
            409, "ACQUISITION_IDENTITY_MISMATCH", "Acquisition and import metadata must match."
        )
    rows = collected.observations
    if len(rows) > 100_000 or not collected.chunks:
        raise APIError(
            422, "EMPTY_OR_OVERSIZED_ACQUISITION", "A bounded validated acquisition is required."
        )
    for chunk in collected.chunks:
        if (
            chunk.failure
            or chunk.provenance is None
            or chunk.status
            not in {"VALIDATED_UNQUALIFIED", "VALIDATED_WITH_GAPS_UNQUALIFIED", "EMPTY_UNQUALIFIED"}
            or chunk.provenance.provider != "DHANHQ"
            or chunk.provenance.listing != collected.listing
        ):
            raise APIError(
                422, "INVALID_ACQUISITION", "Only validated canonical candidates may be imported."
            )
    provenance = plain(
        {
            "plan_fingerprint": collected.plan_fingerprint,
            "unavailable_before_inception": collected.unavailable_before_inception,
            "availability": collected.availability.model_dump(mode="json")
            if collected.availability
            else None,
            "chunks": [chunk.safe_summary() for chunk in collected.chunks],
        }
    )
    # Retrieval timestamps stay in the provenance snapshot, not content identity:
    # repeat same key + same values replays the original immutable audit/provenance.
    payload_hash = digest(
        [
            {
                "values": {
                    k: str(v) if isinstance(v, Decimal) else v
                    for k, v in row.canonical_values().items()
                },
                "source_timestamp": row.provenance.source_timestamp,
            }
            for row in rows
        ]
    )

    def prepare(instrument, source):
        validate_source_policy(source, reference=meta.qualification_ref)
        return prepare_collected(collected, instrument, source)

    return _ingest(
        db,
        meta,
        request_key,
        request_id,
        payload_hash,
        0,
        "provider-daily-candidates",
        prepare,
        expected_source_kind="DHANHQ",
        acquisition_provenance=provenance,
    )


def prepare_collected(collected, instrument, source, *, allow_unassessed_calendar=False):
    rows = collected.observations
    identity = (
        instrument.exchange,
        instrument.symbol,
        instrument.isin,
        instrument.metal,
        instrument.currency,
    )
    listing = collected.listing
    if identity != (
        listing.exchange,
        listing.symbol,
        listing.isin,
        listing.metal,
        listing.currency,
    ):
        raise APIError(
            409, "LISTING_IDENTITY_MISMATCH", "Use the verified exchange listing and ISIN."
        )
    calendar = source.profile.get("calendar")
    if not calendar and not allow_unassessed_calendar:
        raise APIError(409, "SOURCE_CALENDAR_CHANGED", "A matching reviewed calendar is required.")
    for chunk in collected.chunks:
        if calendar is None and allow_unassessed_calendar:
            continue
        batch = chunk.provenance
        expected = {
            day
            for day in calendar["session_dates"]
            if batch.requested_start.isoformat() <= day <= batch.requested_end.isoformat()
        }
        declared = {day.isoformat() for day in chunk.validation.candidate_dates}
        declared.update(day.isoformat() for day in chunk.validation.missing_sessions or ())
        if (
            calendar["version"] != batch.calendar_version
            or calendar["evidence_ref"] != batch.calendar_evidence_reference
            or calendar["coverage_start"] > batch.requested_start.isoformat()
            or calendar["coverage_end"] < batch.requested_end.isoformat()
            or chunk.validation.missing_sessions is None
            or expected != declared
        ):
            raise APIError(
                409, "SOURCE_CALENDAR_CHANGED", "Refresh the reviewed acquisition calendar."
            )
    report = Report(row_count=len(rows))
    for number, row in enumerate(rows, 1):
        try:
            values = row.canonical_values()
            if (
                row.provenance.batch.listing != listing
                or row.provenance.batch.provider != "DHANHQ"
                or not collected.requested_start <= row.trading_date <= collected.requested_end
                or row.interval != "1d"
                or row.price_basis != "PROVIDER_ADJUSTED"
                or row.event_time is not None
                or row.provider_published_at is not None
                or row.event_precision != "SESSION_DATE"
            ):
                raise ValueError()
            for key in ("open", "high", "low", "close"):
                if (
                    type(values[key]) is not Decimal
                    or not values[key].is_finite()
                    or not 0 < values[key] < Decimal("1e14")
                    or values[key].as_tuple().exponent < -10
                ):
                    raise ValueError()
                price(format(values[key], "f"))
            if (
                type(row.volume) is not int
                or not 0 <= row.volume <= 2**63 - 1
                or not row.low <= row.open <= row.high
                or not row.low <= row.close <= row.high
            ):
                raise ValueError()
            calendar = source.profile.get("calendar")
            day = row.trading_date.isoformat()
            if (
                calendar
                and (
                    not calendar["coverage_start"] <= day <= calendar["coverage_end"]
                    or day not in calendar["session_dates"]
                )
            ) or (not calendar and not allow_unassessed_calendar):
                raise ValueError()
            # Retain only validated numeric timestamp evidence, not arbitrary payload text.
            stamp_text = row.provenance.source_timestamp
            if not isinstance(stamp_text, str) or len(stamp_text) > 128:
                raise ValueError()
            stamp = Decimal(stamp_text)
            if (
                not stamp.is_finite()
                or not MIN_CANDIDATE_SECONDS <= stamp <= MAX_CANDIDATE_SECONDS
                or stamp != stamp.to_integral_value()
                or _candidate_nse_date(int(stamp)) != day
            ):
                raise ValueError()
            retrieved = row.provenance.batch.retrieved_at
            if (
                not isinstance(retrieved, datetime)
                or retrieved.tzinfo is None
                or retrieved.utcoffset() is None
                or row.provenance.batch.timestamp_policy != "UNIX_SECONDS_IST_CANDIDATE_V1"
            ):
                raise ValueError()
            raw = {k: plain(v) for k, v in values.items()}
            raw.update(
                source_timestamp=row.provenance.source_timestamp,
                source_row=row.provenance.source_row,
                retrieved_at=plain(row.provenance.batch.retrieved_at),
            )
            h = row.canonical_hash
            report.rows.append((number, raw, h))
            if row.trading_date in report.candidates:
                if report.candidates[row.trading_date][2] == h:
                    report.duplicates += 1
                    report.add(number, "EXACT_DUPLICATE", "INFO")
                else:
                    report.add(number, "CONFLICTING_DUPLICATE")
            else:
                report.candidates[row.trading_date] = (number, values, h)
        except (ValueError, ArithmeticError, AttributeError, TypeError):
            # Invalid payload fields are not retained in import_rows.
            report.add(number, "INVALID_CANONICAL_OBSERVATION")
    if not rows:
        report.add(None, "EMPTY_ACQUISITION")
    for code in (
        "TIMESTAMP_CONTRACT_UNVERIFIED",
        "ADJUSTMENT_METHOD_UNVERIFIED",
        "NO_INDEPENDENT_PRICE_RECONCILIATION",
    ):
        report.add(None, code, "UNASSESSED")
    if collected.missing_sessions:
        report.add(None, "MISSING_SESSIONS", "WARN")
    if collected.unavailable_before_inception:
        report.add(None, "UNAVAILABLE_BEFORE_INCEPTION", "UNASSESSED")
    return report
