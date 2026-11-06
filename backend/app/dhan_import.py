"""Manual backend runner. Default preflight has no network or database connection."""

import argparse
import json
from pathlib import Path
from uuid import UUID, uuid5

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from .acquisition import HistoryPlan, collect_history, preflight
from .config import Settings
from .dhan_config import load_dhan_configuration
from .dhan_provider import DhanDailyProvider
from .errors import APIError
from .models import DataSource, Instrument
from .provider_ingestion import ingest_collected, validate_source_policy
from .schemas import CanonicalImportMetadata
from .serialization import plain


class SafeArguments(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("INVALID_ARGUMENTS")


def main(argv=None, *, provider_factory=None, session_factory=None, pause=None):
    parser = SafeArguments(
        description="Offline preflight by default; explicit reviewed execution required"
    )
    parser.add_argument("--plan", required=True)
    parser.add_argument("--execute-approved-plan")
    parser.add_argument("--persist-approved", action="store_true")
    parser.add_argument("--source-id", type=UUID)
    parser.add_argument("--run-id", type=UUID)
    parser.add_argument("--env-file", default=".env")
    try:
        args = parser.parse_args(argv)
        path = Path(args.plan)
        if path.stat().st_size > 1_000_000:
            raise ValueError()
        with path.open("rb") as stream:
            plan_bytes = stream.read(1_000_001)
        if len(plan_bytes) > 1_000_000:
            raise ValueError()
        plan = HistoryPlan.model_validate_json(plan_bytes)
        config = load_dhan_configuration(
            env_file=Path(args.env_file) if Path(args.env_file).is_file() else None
        )
        provider = (provider_factory or DhanDailyProvider)(config)
        report = preflight(provider, plan)
        report["configuration"] = {
            "enabled": config.enabled,
            "valid": config.values_valid,
            "access_token_present": config.access_token_present,
        }
        if args.execute_approved_plan is None:
            print(json.dumps(report))
            return 0
        if args.execute_approved_plan != report["plan_fingerprint"]:
            print(
                json.dumps({"status": "BLOCKED", "code": "REVIEWED_PLAN_MISMATCH", "requests": 0})
            )
            return 2
        if args.persist_approved and (args.source_id is None or args.run_id is None):
            raise ValueError()
        # Resolve licences/policy/listing identities before any provider request.
        engine, db, targets, reference = None, None, {}, None
        try:
            if args.persist_approved:
                if session_factory is not None:
                    db = session_factory()
                else:
                    settings = Settings(_env_file=args.env_file)
                    engine = create_engine(settings.database_url)
                    db = Session(engine)
                source = db.get(DataSource, args.source_id)
                if source is None:
                    raise APIError(
                        404, "SOURCE_NOT_FOUND", "Register a reviewed provider source first."
                    )
                validate_source_policy(source)
                reference = source.rights_evidence_ref
                for listing in provider.listings():
                    instrument = db.scalar(
                        select(Instrument).where(
                            Instrument.exchange == listing.exchange,
                            Instrument.symbol == listing.symbol,
                            Instrument.isin == listing.isin,
                            Instrument.currency == listing.currency,
                            Instrument.metal == listing.metal,
                        )
                    )
                    if instrument is None:
                        raise APIError(
                            409, "LISTING_IDENTITY_MISMATCH", "Register all four verified listings."
                        )
                    targets[listing.symbol] = instrument.id
                db.rollback()  # No database transaction spans network retrieval.
            options = {"request_approved": True}
            if pause is not None:
                options["pause"] = pause
            result = collect_history(provider, plan, **options)
            if result.status != "COLLECTED_UNQUALIFIED":
                print(json.dumps(result.safe_summary()))
                return 1
            imports = []
            if args.persist_approved:
                for series in result.series:
                    if not series.chunks:
                        imports.append(
                            {"symbol": series.listing.symbol, "status": "BEFORE_INCEPTION_NO_WRITE"}
                        )
                        continue
                    key = uuid5(args.run_id, series.listing.isin)
                    meta = CanonicalImportMetadata(
                        instrument_id=targets[series.listing.symbol],
                        source_id=args.source_id,
                        qualification_ref=reference,
                        plan_fingerprint=report["plan_fingerprint"],
                        requested_start=plan.start,
                        requested_end=plan.end,
                    )
                    status, payload = ingest_collected(
                        db, series, meta, key, str(args.run_id), persistence_approved=True
                    )
                    batch = payload["data"]
                    imports.append(
                        {
                            "symbol": series.listing.symbol,
                            "http_status": status,
                            "batch_id": plain(batch["id"]),
                            "status": batch["status"],
                            "new_count": batch["new_count"],
                            "duplicate_count": batch["duplicate_count"],
                            "replayed": batch["replayed"],
                        }
                    )
                    if batch["status"] == "REJECTED":
                        print(
                            json.dumps(
                                {
                                    "status": "IMPORT_STOPPED",
                                    "imports": imports,
                                    "recovery": "RESOLVE_BATCH_BY_STABLE_REQUEST_KEY",
                                }
                            )
                        )
                        return 1
            print(
                json.dumps(
                    {
                        "collection": result.safe_summary(),
                        "imports": imports,
                        "persistence": "EXPLICITLY_APPROVED"
                        if args.persist_approved
                        else "NOT_REQUESTED_NO_DATABASE",
                    }
                )
            )
            return 0
        finally:
            if db is not None:
                db.close()
            if engine is not None:
                engine.dispose()
    except APIError as error:
        print(
            json.dumps(
                {
                    "status": "STOPPED",
                    "code": error.code,
                    "recovery": "QUERY_IMPORT_BATCH_WITH_RUN_DERIVED_REQUEST_KEY_BEFORE_RETRY",
                }
            )
        )
        return 1
    except Exception:
        # No exception text, DB URLs, CLI values, credentials or market payloads.
        print(
            json.dumps(
                {
                    "status": "STOPPED",
                    "code": "SAFE_EXECUTION_ERROR",
                    "recovery": "QUERY_IMPORT_BATCH_WITH_RUN_DERIVED_REQUEST_KEY_BEFORE_RETRY",
                }
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
