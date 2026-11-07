"""Process-memory retention sink for owner-authorized transient research. No file/SQL I/O.

Canonical validation and all analytical/quality calculations are shared with imports.
Registry publication is atomic. Acquisition is delegated to the market-data service.
"""

from threading import RLock
from uuid import NAMESPACE_URL, uuid4, uuid5

from .analytics import Point
from .errors import APIError
from .models import DataSource, Instrument, Observation, now
from .provider_ingestion import prepare_collected
from .queries import describe_series
from .serialization import digest, plain


class TransientResearch:
    def __init__(self):
        self._lock = RLock()
        self._claimed = False
        self._datasets = {}
        self._report = {"status": "NOT_LOADED", "live_requests": 0}
        self.revision = "empty"

    def snapshot(self):
        """Read request gets one immutable dataset publication, including its revision."""
        with self._lock:
            view = TransientResearch()
            view._datasets = self._datasets.copy()
            view._report = self._report.copy()
            view.revision = self.revision
            return view

    def claim(self):
        with self._lock:
            if self._claimed:
                raise APIError(
                    409,
                    "LIVE_RUN_ALREADY_ATTEMPTED",
                    "The process live-request budget was already claimed. No retry was made.",
                )
            self._claimed = True

    def report(self):
        with self._lock:
            report = self._report.copy()
            if self._datasets and report["status"] == "NOT_LOADED":
                report.update(
                    status="READY_TRANSIENT_UNQUALIFIED"
                    if any(d["rows"] for d in self._datasets.values())
                    else "CONFIGURED_TRANSIENT_EMPTY",
                    persistence="NONE_PROCESS_MEMORY_ONLY",
                    owner_uat="PENDING",
                    source_id=str(next(iter(self._datasets.values()))["source"].id),
                    instruments=[
                        {
                            "symbol": d["instrument"].symbol,
                            "instrument_id": str(d["instrument"].id),
                            "source_id": str(d["source"].id),
                            "observations": len(d["rows"]),
                            "earliest": plain(d["rows"][0].trading_date) if d["rows"] else None,
                            "latest": plain(d["rows"][-1].trading_date) if d["rows"] else None,
                        }
                        for d in self._datasets.values()
                    ],
                )
            return report

    def record_failure(self, summary):
        with self._lock:
            self._report = summary

    def install(self, collection, plan, *, names, data_class="REAL_MARKET"):
        """Publish only shared-validator-approved canonical candidates, without SQL writes."""
        if collection.status != "COLLECTED_UNQUALIFIED":
            raise APIError(
                422, "INVALID_COLLECTION", "Only validated collections can be retained transiently."
            )
        datasets = {}
        source_id = uuid4()
        stamp = now()
        source = DataSource(
            id=source_id,
            label="DhanHQ — real historical data — transient memory"
            if data_class == "REAL_MARKET"
            else "SYNTHETIC transient fixture",
            source_kind="DHANHQ",
            contract_version="dhan-daily-v1-provisional",
            qualification="TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED",
            rights_evidence_ref="Owner Step 5D.3 authorization: transient private research only",
            permitted_uses={"retrieval": True, "storage": False, "analysis": True, "display": True},
            reviewed_at=stamp,
            profile={
                "data_class": data_class,
                "policy_version": "quality-v1",
                "calendar": plan.calendar.model_dump(mode="json"),
                "known_break_dates": [],
                "freshness": None,
                "adjustment_definition_ref": collection.series[0]
                .chunks[0]
                .provenance.adjustment_reference,
                "acquisition_review": {
                    "timestamp_policy": "UNIX_SECONDS_IST_CANDIDATE_V1",
                    "allow_provisional_session_dates": True,
                    "review_ref": "Owner-authorized transient inspection; semantics unverified",
                },
            },
        )
        summaries = []
        for series in collection.series:
            listing = series.listing
            identifier = uuid5(
                NAMESPACE_URL, "bullion-transient:" + str(source_id) + ":" + listing.isin
            )
            instrument = Instrument(
                id=identifier,
                exchange=listing.exchange,
                symbol=listing.symbol,
                isin=listing.isin,
                name=names[listing.symbol],
                metal=listing.metal,
                currency=listing.currency,
                active=True,
                data_revision=1,
                created_at=stamp,
                updated_at=stamp,
            )
            report = prepare_collected(series, instrument, source)
            if report.errors:
                raise APIError(
                    422,
                    "INVALID_CANONICAL_COLLECTION",
                    "Canonical validation rejected the transient collection.",
                )
            batch_id = uuid4()
            rows = tuple(
                Observation(
                    id=uuid5(batch_id, str(day)),
                    instrument_id=identifier,
                    source_id=source_id,
                    batch_id=batch_id,
                    row_number=number,
                    canonical_hash=h,
                    ingested_at=stamp,
                    **values,
                )
                for day, (number, values, h) in sorted(report.candidates.items())
            )
            datasets[(identifier, source_id)] = {
                "instrument": instrument,
                "source": source,
                "rows": rows,
                "collected": series,
                "issues": tuple(report.issues),
            }
            summaries.append(
                {
                    "symbol": listing.symbol,
                    "instrument_id": str(identifier),
                    "source_id": str(source_id),
                    "observations": len(rows),
                    "earliest": plain(rows[0].trading_date) if rows else None,
                    "latest": plain(rows[-1].trading_date) if rows else None,
                    "missing_sessions": plain(series.missing_sessions),
                    "canonical_invalid_count": report.errors,
                }
            )
        with self._lock:
            self._datasets = datasets
            self.revision = digest(
                {"source": str(source_id), "plan": collection.series[0].plan_fingerprint}
            )
            self._report = {
                "status": "READY_TRANSIENT_UNQUALIFIED",
                "live_requests": collection.attempted_requests,
                "persistence": "NONE_PROCESS_MEMORY_ONLY",
                "source_id": str(source_id),
                "instruments": summaries,
                "acquisition": collection.safe_summary(),
                "owner_uat": "PENDING",
            }
        return self.report()

    def configure(self, listings, calendar, *, data_class="REAL_MARKET", names=None):
        """Register verified provider identities without fetching data or creating SQL rows."""
        from .dhan_history_contract import ADJUSTMENT_REF

        with self._lock:
            if self._datasets:
                return
            source_id, stamp = uuid4(), now()
            source = DataSource(
                id=source_id,
                label="DhanHQ - real historical data - transient memory"
                if data_class == "REAL_MARKET"
                else "SYNTHETIC transient fixture",
                source_kind="DHANHQ",
                contract_version="dhan-daily-v1-provisional",
                qualification="TRANSIENT_OWNER_AUTHORIZED_UNQUALIFIED",
                rights_evidence_ref="Step 5D.4 standing read-only authorization; no persistent license",
                permitted_uses={
                    "retrieval": True,
                    "storage": False,
                    "analysis": True,
                    "display": True,
                },
                reviewed_at=stamp,
                profile={
                    "data_class": data_class,
                    "policy_version": "quality-v1",
                    "calendar": calendar.model_dump(mode="json") if calendar else None,
                    "known_break_dates": [],
                    "freshness": None,
                    "adjustment_definition_ref": ADJUSTMENT_REF,
                    "acquisition_review": {
                        "timestamp_policy": "UNIX_SECONDS_IST_CANDIDATE_V1",
                        "allow_provisional_session_dates": True,
                        "review_ref": "Owner-authorized transient research; semantics unverified",
                    },
                },
            )
            for listing in listings:
                identifier = uuid5(
                    NAMESPACE_URL, "bullion-transient:" + str(source_id) + ":" + listing.isin
                )
                instrument = Instrument(
                    id=identifier,
                    exchange=listing.exchange,
                    symbol=listing.symbol,
                    isin=listing.isin,
                    name=(names or {}).get(listing.symbol, listing.symbol),
                    metal=listing.metal,
                    currency=listing.currency,
                    active=True,
                    data_revision=0,
                    created_at=stamp,
                    updated_at=stamp,
                )
                self._datasets[(identifier, source_id)] = {
                    "instrument": instrument,
                    "source": source,
                    "rows": (),
                    "collected": None,
                    "issues": (),
                    "provenance": (),
                }
            self.revision = digest({"source": str(source_id)})

    def merge(self, instrument_id, source_id, collected, *, max_rows=100000, refresh=False):
        """Use the same canonical validator as persistent ingestion; publish atomically.

        Revisions replace matching dates only on explicit refresh/staleness revalidation.
        Historical and new provenance records remain attached, bounded by the service.
        """
        from types import SimpleNamespace

        with self._lock:
            data = self._datasets[(instrument_id, source_id)]
            source = data["source"]
            profile = dict(source.profile)
            if any(c.provenance.calendar_version is None for c in collected.chunks):
                profile["calendar"] = None
            view = SimpleNamespace(profile=profile)
            report = prepare_collected(
                collected, data["instrument"], view, allow_unassessed_calendar=True
            )
            if report.errors:
                raise APIError(
                    422,
                    "INVALID_CANONICAL_COLLECTION",
                    "Canonical validation rejected observations.",
                )
            existing = {r.trading_date: r for r in data["rows"]}
            conflicts = [
                d
                for d, (_, _, h) in report.candidates.items()
                if d in existing and existing[d].canonical_hash != h
            ]
            if conflicts and not refresh:
                raise APIError(
                    409,
                    "PROVIDER_REVISION_REQUIRES_REFRESH",
                    "Existing values differ. Use explicit provider refresh to accept validated revisions.",
                )
            total = sum(len(d["rows"]) for d in self._datasets.values())
            additions = sum(d not in existing for d in report.candidates)
            if total + additions > max_rows:
                raise APIError(
                    409,
                    "MEMORY_LIMIT",
                    "Transient observation capacity reached; narrow the request or restart knowingly.",
                )
            batch, stamp, changed = uuid4(), now(), 0
            for day, (number, values, h) in report.candidates.items():
                if day in existing and existing[day].canonical_hash == h:
                    continue
                existing[day] = Observation(
                    id=uuid5(batch, str(day)),
                    instrument_id=instrument_id,
                    source_id=source_id,
                    batch_id=batch,
                    row_number=number,
                    canonical_hash=h,
                    ingested_at=stamp,
                    **values,
                )
                changed += 1
            provenance = tuple(data.get("provenance", ())) + tuple(
                {
                    "batch_id": str(batch),
                    "summary": plain(c.safe_summary()),
                    "observation_provenance": tuple(r.provenance for r in c.observations),
                }
                for c in collected.chunks
            )
            # Keep exact original evidence for retained observations, plus a bounded revision trail.
            retained_evidence = sum(
                len(p.get("observation_provenance", ()))
                for item in self._datasets.values()
                for p in item.get("provenance", ())
            )
            new_evidence = sum(len(c.observations) for c in collected.chunks)
            if len(provenance) > 2048 or retained_evidence + new_evidence > max_rows * 2:
                raise APIError(409, "PROVENANCE_LIMIT", "Transient provenance capacity reached.")
            data = {
                **data,
                "rows": tuple(existing[d] for d in sorted(existing)),
                "provenance": provenance,
            }
            if changed:
                from copy import copy

                instrument = copy(data["instrument"])
                instrument.data_revision += 1
                instrument.updated_at = stamp
                data["instrument"] = instrument
                self.revision = digest({"previous": self.revision, "batch": str(batch)})
            self._datasets = {**self._datasets, (instrument_id, source_id): data}
            return {
                "added": additions,
                "revised": len(conflicts),
                "changed": changed,
                "dataset_count": len(existing),
            }

    def listings(self, metal=None):
        return tuple(
            d["instrument"]
            for d in tuple(self._datasets.copy().values())
            if metal is None or d["instrument"].metal == metal
        )

    def sources(self):
        return tuple({d["source"].id: d["source"] for d in self._datasets.values()}.values())

    def has_series(self, instrument_id, source_id):
        return (instrument_id, source_id) in self._datasets

    def series(self, instrument_id, source_id):
        data = self._datasets[(instrument_id, source_id)]
        return data["instrument"], data["source"]

    def rows(self, instrument_id, source_id, basis, start=None, end=None):
        if basis != "PROVIDER_ADJUSTED":
            return ()
        return tuple(
            r
            for r in self._datasets[(instrument_id, source_id)]["rows"]
            if (start is None or r.trading_date >= start) and (end is None or r.trading_date <= end)
        )

    def points(self, instrument_id, source_id, basis, start=None, end=None):
        return [
            Point(
                r.trading_date,
                r.close,
                str(r.id),
                r.canonical_hash,
                str(r.batch_id),
                r.row_number,
                r.volume,
            )
            for r in self.rows(instrument_id, source_id, basis, start, end)
        ]

    def meta(self, instrument, source, basis, start, end, assessment=None):
        all_rows = self.rows(instrument.id, source.id, basis)
        rows = self.rows(instrument.id, source.id, basis, start, end)
        meta = describe_series(
            instrument,
            source,
            basis,
            start,
            end,
            assessment,
            all_rows[0].trading_date if all_rows else None,
            all_rows[-1].trading_date if all_rows else None,
            len(all_rows),
            rows[0].trading_date if rows else None,
            rows[-1].trading_date if rows else None,
            len(rows),
            [r.trading_date for r in rows],
            len(all_rows),
            {"UNASSESSED": 3},
        )
        meta["quality"]["flags"].extend(
            ["TRANSIENT_MEMORY_ONLY", "PERSISTENT_USE_PERMISSION_UNRESOLVED"]
        )
        meta["limitations"].extend(
            [
                "TRANSIENT_ONLY_NO_PERSISTENCE",
                "DATA_LOST_ON_BACKEND_RESTART",
                "SOURCE_NOT_FULLY_QUALIFIED",
            ]
        )
        meta["source"]["verification"] = "OWNER_AUTHORIZED_TRANSIENT_RESEARCH_NOT_SOURCE_ACCEPTANCE"
        if source.profile.get("handoff_limitation"):
            meta["limitations"].append("HANDOFF_ORIGINAL_NUMERIC_EPOCH_UNAVAILABLE")
        return meta
