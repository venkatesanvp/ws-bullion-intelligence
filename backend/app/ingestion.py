import csv
import hashlib
import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select, text
from .daily_values import price
from .errors import APIError
from .models import DataSource, ImportBatch, ImportRow, Instrument, Observation, QualityResult
from .schemas import ImportMetadata
from .serialization import digest, plain


@dataclass
class Report:
    rows: list = field(default_factory=list)
    candidates: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    errors: int = 0
    duplicates: int = 0
    conflict: bool = False
    row_count: int = 0

    def add(self, row, code, severity="ERROR", field_name=None):
        if code == "CONFLICTING_DUPLICATE":
            self.conflict = True
        if severity == "ERROR":
            self.errors += 1
        if len(self.issues) < 1000:
            self.issues.append(
                {
                    "row_number": row,
                    "code": code,
                    "severity": severity,
                    "details": {"field": field_name} if field_name else {},
                }
            )


def instant(value: str):
    if not value:
        return None
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError()
    return d.astimezone(timezone.utc)


def parse_csv(
    content: bytes, meta: ImportMetadata, instrument: Instrument, source: DataSource, max_rows: int
) -> Report:
    result = Report()
    if b"\x00" in content:
        result.add(None, "INVALID_TEXT")
        return result
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        result.add(None, "INVALID_UTF8")
        return result
    reader = csv.DictReader(io.StringIO(decoded, newline=""), strict=True)
    try:
        headers = reader.fieldnames
        if (
            not headers
            or len(headers) != len(set(headers))
            or set(headers) != set(meta.column_map.values())
        ):
            result.add(None, "HEADER_MISMATCH")
            return result
        previous = None
        out_of_order = False
        for number, row in enumerate(reader, 1):
            result.row_count = number
            if number > max_rows:
                result.add(None, "ROW_LIMIT_EXCEEDED")
                return result
            if None in row or any(v is None for v in row.values()):
                result.add(number, "COLUMN_COUNT_MISMATCH")
                continue
            raw = {key: row[header] for key, header in meta.column_map.items()}
            normalized = {}
            before = result.errors
            if any(len(v) > 1024 for v in raw.values()):
                result.add(number, "FIELD_TOO_LONG")
                continue
            for key in [
                "trading_date",
                "close",
                "open",
                "high",
                "low",
                "volume",
                "symbol",
                "currency",
                "provider_published_at",
                "event_time",
            ]:
                value = raw.get(key, "").strip()
                try:
                    if key == "trading_date":
                        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                            raise ValueError()
                        normalized[key] = date.fromisoformat(value)
                    elif key in {"close", "open", "high", "low"}:
                        normalized[key] = price(value) if value else None
                        if key == "close" and normalized[key] is None:
                            raise ValueError()
                    elif key == "volume":
                        if value and (
                            not re.fullmatch(r"\d+", value) or int(value) > 9223372036854775807
                        ):
                            raise ValueError()
                        normalized[key] = int(value) if value else None
                    elif key == "symbol" and value and value != instrument.symbol:
                        raise ValueError()
                    elif key == "currency" and value and value != instrument.currency:
                        raise ValueError()
                    elif key in {"provider_published_at", "event_time"}:
                        normalized[key] = instant(value)
                except (ValueError, OverflowError):
                    result.add(number, "INVALID_" + key.upper(), field_name=key)
            if result.errors == before:
                opening, high, low, close = (
                    normalized[x] for x in ("open", "high", "low", "close")
                )
                if any(x is not None for x in (opening, high, low)) and (
                    any(x is None for x in (opening, high, low))
                    or high < max(opening, low, close)
                    or low > min(opening, high, close)
                ):
                    result.add(number, "INVALID_OHLC")
                calendar = source.profile.get("calendar")
                day = normalized["trading_date"].isoformat()
                if (
                    calendar
                    and calendar["coverage_start"] <= day <= calendar["coverage_end"]
                    and day not in calendar["session_dates"]
                ):
                    result.add(number, "NON_TRADING_DATE")
                if previous is not None and normalized["trading_date"] < previous:
                    out_of_order = True
                previous = normalized["trading_date"]
            content_hash = None
            if result.errors == before:
                normalized["event_precision"] = (
                    "INSTANT" if normalized["event_time"] else "SESSION_DATE"
                )
                normalized["interval"] = meta.interval
                normalized["price_basis"] = meta.price_basis
                # Canonicalize numerically identical decimal spellings without changing raw strings.
                hash_values = {
                    k: format(v.normalize(), "f") if isinstance(v, Decimal) else v
                    for k, v in normalized.items()
                }
                content_hash = digest(hash_values)
                day = normalized["trading_date"]
                if day in result.candidates:
                    if result.candidates[day][2] == content_hash:
                        result.duplicates += 1
                        result.add(number, "EXACT_DUPLICATE", "INFO")
                    else:
                        result.add(number, "CONFLICTING_DUPLICATE")
                else:
                    result.candidates[day] = (number, normalized, content_hash)
            result.rows.append((number, raw, content_hash))
        if out_of_order:
            result.add(None, "OUT_OF_ORDER_NORMALIZED", "INFO")
    except (csv.Error, UnicodeError):
        result.add(None, "INVALID_CSV")
    return result


def batch_data(batch: ImportBatch, *, replayed=False):
    value = plain(batch)
    value["replayed"] = replayed
    value["diagnostics_may_be_limited"] = batch.error_count > 1000
    value["data_class"] = batch.profile_snapshot.get("source_profile", {}).get(
        "data_class", "UNKNOWN"
    )
    value["source_verification"] = "OWNER_RECORDED_NOT_THIRD_PARTY_VERIFIED"
    return value


def batch_response(batch: ImportBatch, replayed=False):
    data = batch_data(batch, replayed=replayed)
    if batch.status == "REJECTED":
        code = batch.error_code or "IMPORT_REJECTED"
        return (409 if code == "CONFLICTING_DUPLICATE" else 422), {
            "error": {
                "code": code,
                "message": "Import rejected. No new observations were stored.",
                "request_id": batch.request_id,
                "details": [],
            },
            "data": data,
        }
    return (200 if replayed else 201), {"data": data}


def ingest(
    db,
    content: bytes,
    filename: str,
    meta: ImportMetadata,
    request_key: UUID,
    request_id: str,
    max_rows: int,
):
    return _ingest(
        db,
        meta,
        request_key,
        request_id,
        hashlib.sha256(content).hexdigest(),
        len(content),
        filename,
        lambda instrument, source: parse_csv(content, meta, instrument, source, max_rows),
        expected_source_kind="USER_CSV",
    )


def _ingest(
    db,
    meta,
    request_key,
    request_id,
    file_hash,
    byte_count,
    filename,
    prepare_report,
    *,
    expected_source_kind,
    acquisition_provenance=None,
):
    """Shared atomic repository path for CSV and validated canonical acquisitions."""
    request_meta = meta.model_dump(mode="json")
    lock_key = int.from_bytes(hashlib.sha256(request_key.bytes).digest()[:8], "big", signed=True)
    with db.begin():
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})
        old = db.scalar(select(ImportBatch).where(ImportBatch.request_key == request_key))
        if old:
            if old.file_sha256 != file_hash or old.profile_snapshot["request"] != request_meta:
                raise APIError(
                    409,
                    "IDEMPOTENCY_KEY_REUSED",
                    "Use a new request key for different content or metadata.",
                )
            return batch_response(old, replayed=True)
        source = db.scalar(
            select(DataSource).where(DataSource.id == meta.source_id).with_for_update(read=True)
        )
        instrument = db.scalar(
            select(Instrument).where(Instrument.id == meta.instrument_id).with_for_update()
        )
        if source is None or instrument is None:
            raise APIError(404, "NOT_FOUND", "Instrument or source not found.")
        if source.source_kind != expected_source_kind:
            raise APIError(409, "SOURCE_KIND_MISMATCH", "Choose the matching source contract.")
        uses = source.permitted_uses
        if (
            source.qualification != "QUALIFIED_FOR_RESEARCH"
            or not all(uses.get(k) for k in ("retrieval", "storage", "analysis", "display"))
            or not uses.get("retention_review_ref")
        ):
            raise APIError(
                403,
                "SOURCE_NOT_QUALIFIED",
                "Record source-use and retention evidence before importing.",
            )
        if (
            meta.qualification_ref != source.rights_evidence_ref
            or meta.quality_policy_version != source.profile["policy_version"]
        ):
            raise APIError(
                409, "SOURCE_PROFILE_CHANGED", "Refresh the source qualification and policy."
            )
        if meta.price_basis == "PROVIDER_ADJUSTED" and not source.profile.get(
            "adjustment_definition_ref"
        ):
            raise APIError(
                422,
                "BASIS_UNVERIFIED",
                "An adjusted series requires its source adjustment definition.",
            )
        report = prepare_report(instrument, source)
        if not report.rows and not report.errors:
            report.add(None, "EMPTY_FILE")
        if not source.profile.get("calendar"):
            report.add(None, "CALENDAR_UNVERIFIED", "UNASSESSED")
        if not source.profile.get("adjustment_definition_ref"):
            report.add(None, "CORPORATE_ACTIONS_UNASSESSED", "UNASSESSED")
        existing = (
            {
                x.trading_date: x
                for x in db.scalars(
                    select(Observation).where(
                        Observation.instrument_id == instrument.id,
                        Observation.source_id == source.id,
                        Observation.interval == meta.interval,
                        Observation.price_basis == meta.price_basis,
                        Observation.trading_date >= min(report.candidates),
                        Observation.trading_date <= max(report.candidates),
                    )
                )
            }
            if report.candidates and not report.errors
            else {}
        )
        pending = []
        for day, (number, values, content_hash) in sorted(report.candidates.items()):
            if day in existing:
                if existing[day].canonical_hash == content_hash:
                    report.duplicates += 1
                    report.add(number, "EXACT_DUPLICATE", "INFO")
                else:
                    report.add(number, "CONFLICTING_DUPLICATE")
            else:
                pending.append((number, values, content_hash))
        conflict = report.conflict
        snapshot = {
            "request": request_meta,
            "source_profile": source.profile,
            "rights_evidence_ref": source.rights_evidence_ref,
            "permitted_uses": uses,
            "reviewed_at": plain(source.reviewed_at),
            **({"acquisition": acquisition_provenance} if acquisition_provenance else {}),
        }
        batch = ImportBatch(
            request_key=request_key,
            instrument_id=instrument.id,
            source_id=source.id,
            file_sha256=file_hash,
            profile_sha256=digest(snapshot),
            profile_snapshot=snapshot,
            status="REJECTED" if report.errors else ("ACCEPTED" if pending else "NO_CHANGE"),
            bytes=byte_count,
            row_count=report.row_count,
            new_count=0 if report.errors else len(pending),
            duplicate_count=report.duplicates,
            error_count=report.errors,
            sanitized_name=filename[:256],
            request_id=request_id,
            error_code=("CONFLICTING_DUPLICATE" if conflict else "IMPORT_VALIDATION_FAILED")
            if report.errors
            else None,
        )
        db.add(batch)
        db.flush()
        for number, raw, content_hash in report.rows:
            db.add(
                ImportRow(
                    batch_id=batch.id,
                    row_number=number,
                    mapped_raw=raw,
                    canonical_hash=content_hash,
                )
            )
        db.flush()
        recorded_rows = {r[0] for r in report.rows}
        for issue in report.issues:
            row_number = issue["row_number"] if issue["row_number"] in recorded_rows else None
            details = dict(issue["details"])
            if row_number is None and issue["row_number"] is not None:
                details["input_row_number"] = issue["row_number"]
            db.add(
                QualityResult(
                    batch_id=batch.id,
                    row_number=row_number,
                    code=issue["code"],
                    severity=issue["severity"],
                    details=details,
                )
            )
        if not report.errors:
            for number, values, content_hash in pending:
                db.add(
                    Observation(
                        instrument_id=instrument.id,
                        source_id=source.id,
                        batch_id=batch.id,
                        row_number=number,
                        canonical_hash=content_hash,
                        **values,
                    )
                )
            if pending:
                instrument.data_revision += 1
        db.flush()
        response = batch_response(batch)
    return response
