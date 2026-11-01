"""VS01-T-22: binary backup/restore using only the disposable test-db service.

REQ-05-009 / REQ-06-008 -> ADR-09 -> DC-09 -> current Step 3 recovery grant.
Never reads, writes, drops or switches the active application database.
"""

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
import psycopg  # noqa: E402
from psycopg import sql  # noqa: E402
from sqlalchemy.engine import URL  # noqa: E402
from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402

TOKEN = "synthetic-recovery-test-token-not-a-secret-000000"
ORIGIN = "http://127.0.0.1:5173"
TABLES = (
    "alembic_version",
    "instruments",
    "data_sources",
    "watchlists",
    "watchlist_members",
    "import_batches",
    "import_rows",
    "price_observations",
    "quality_results",
)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def normalized_constraint(table, name, definition):
    # PostgreSQL 18 dump/reparse distributes a varchar[] -> text[] cast over
    # each enum literal. Accept only the two exact equivalent deparses of
    # the five existing checks; all other definitions remain byte-compared.
    enums = {
        ("data_sources", "ck_qualification"): (
            "qualification",
            ["UNVERIFIED", "QUALIFIED_FOR_RESEARCH", "RESTRICTED"],
        ),
        ("import_batches", "ck_batch_status"): (
            "status",
            ["ACCEPTED", "NO_CHANGE", "REJECTED", "FAILED"],
        ),
        ("instruments", "ck_metal"): ("metal", ["GOLD", "SILVER"]),
        ("price_observations", "ck_basis"): (
            "price_basis",
            ["RAW_CLOSE", "PROVIDER_ADJUSTED", "UNKNOWN"],
        ),
        ("quality_results", "ck_severity"): ("severity", ["ERROR", "WARN", "INFO", "UNASSESSED"]),
    }
    if (table, name) in enums:
        column, values = enums[(table, name)]
        array = ", ".join("'" + value + "'::character varying" for value in values)
        distributed = ", ".join("('" + value + "'::character varying)::text" for value in values)
        original = "CHECK (((" + column + ")::text = ANY ((ARRAY[" + array + "])::text[])))"
        restored = "CHECK (((" + column + ")::text = ANY (ARRAY[" + distributed + "])))"
        if definition in (original, restored):
            definition = "TEXT_ENUM:" + column + ":" + ",".join(values)
    return table, name, definition


def main():
    os.chdir(ROOT)
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "data_class": "SYNTHETIC_TEST",
        "checks": [],
        "success": False,
    }
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    docker = shutil.which("docker") or "C:/Program Files/Docker/Docker/resources/bin/docker.exe"

    def compose(*args, data=None):
        result = subprocess.run(
            [docker, "compose", *args],
            input=data,
            capture_output=True,
            cwd=ROOT,
            timeout=120,
            check=False,
        )
        if result.returncode:
            raise RuntimeError("Docker recovery command failed; no credentials logged")
        return result.stdout

    def checked(name):
        report["checks"].append({"check": name, "passed": True})
        print("PASS: " + name, flush=True)

    try:
        local = dict(
            line.split("=", 1)
            for line in (ROOT / ".env").read_text().splitlines()
            if "=" in line and not line.startswith("#")
        )
        compose("--profile", "test", "up", "-d", "--wait", "test-db")
        marker = compose("exec", "-T", "test-db", "printenv", "POSTGRES_DB").decode().strip()
        if marker != "bullion_test":
            raise RuntimeError("Refusing recovery outside the disposable test service")
        checked("Disposable service identity")
        run_id = uuid4().hex[:12]
        source = "bullion_recovery_source_" + run_id + "_test"
        target = "bullion_recovery_restored_" + run_id + "_test"
        if source == target or not all(
            n.startswith("bullion_recovery_") and n.endswith("_test") for n in (source, target)
        ):
            raise RuntimeError("Recovery database name guard failed")
        report.update(source_database=source, restored_database=target)
        credentials = {
            "host": "127.0.0.1",
            "port": 55433,
            "user": local["POSTGRES_USER"],
            "password": local["POSTGRES_PASSWORD"],
        }
        with psycopg.connect(dbname="bullion_test", autocommit=True, **credentials) as admin:
            admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(source)))

        def database_url(name):
            return URL.create(
                "postgresql+psycopg",
                username=credentials["user"],
                password=credentials["password"],
                host="127.0.0.1",
                port=55433,
                database=name,
            ).render_as_string(hide_password=False)

        os.environ["DATABASE_URL"] = database_url(source)
        os.environ["LOCAL_APP_TOKEN"] = TOKEN
        command.upgrade(Config(str(ROOT / "backend/alembic.ini")), "head")

        def client_for(name):
            settings = Settings(
                _env_file=None,
                database_url=database_url(name),
                local_app_token=TOKEN,
                allowed_hosts="127.0.0.1,localhost,testserver",
            )
            return TestClient(
                create_app(settings), headers={"Authorization": "Bearer " + TOKEN, "Origin": ORIGIN}
            )

        def create(client, resource, body):
            response = client.post("/api/v1/" + resource, json=body)
            if response.status_code != 201:
                raise RuntimeError("Synthetic setup request failed")
            return response.json()["data"]

        with client_for(source) as client:
            listing = create(
                client,
                "instruments",
                {
                    "exchange": "XNSE",
                    "symbol": "SYNTH_RECOVERY",
                    "name": "SYNTHETIC TEST ONLY recovery fixture",
                    "metal": "GOLD",
                    "currency": "INR",
                },
            )
            provider = create(
                client,
                "data-sources",
                {
                    "label": "SYNTHETIC_TEST recovery fixture",
                    "profile": {"data_class": "SYNTHETIC_TEST", "policy_version": "quality-v1"},
                },
            )
            response = client.patch(
                "/api/v1/data-sources/" + provider["id"] + "/qualification",
                json={
                    "qualification": "QUALIFIED_FOR_RESEARCH",
                    "rights_evidence_ref": "Generated synthetic test only",
                    "retention_review_ref": "Disposable recovery exercise",
                    "permitted_uses": dict.fromkeys(
                        ["retrieval", "storage", "analysis", "display"], True
                    ),
                },
            )
            if response.status_code != 200:
                raise RuntimeError("Synthetic qualification failed")
            watchlist = create(client, "watchlists", {"name": "SYNTHETIC recovery watchlist"})
            response = client.post(
                "/api/v1/watchlists/" + watchlist["id"] + "/members",
                json={"instrument_id": listing["id"]},
            )
            if response.status_code not in (200, 201):
                raise RuntimeError("Synthetic watchlist failed")
            metadata = {
                "instrument_id": listing["id"],
                "source_id": provider["id"],
                "interval": "1d",
                "price_basis": "RAW_CLOSE",
                "mapping_version": "test-v1",
                "column_map": {"trading_date": "trading_date", "close": "close"},
                "quality_policy_version": "quality-v1",
                "qualification_ref": "Generated synthetic test only",
            }
            response = client.post(
                "/api/v1/import-batches",
                files={
                    "file": (
                        "synthetic-recovery.csv",
                        b"trading_date,close\n2026-01-01,10.1234567890\n2026-01-02,12\n2026-01-03,11\n",
                        "text/csv",
                    )
                },
                data={"metadata_json": json.dumps(metadata)},
                headers={"Idempotency-Key": str(uuid4())},
            )
            if response.status_code != 201:
                raise RuntimeError("Synthetic import failed")
            second_listing = create(
                client,
                "instruments",
                {
                    "exchange": "XNSE",
                    "symbol": "SYNTH_RECOVERY_SILVER",
                    "name": "SYNTHETIC TEST ONLY silver recovery fixture",
                    "metal": "SILVER",
                    "currency": "INR",
                },
            )
            response = client.post(
                "/api/v1/import-batches",
                files={
                    "file": (
                        "synthetic-silver-recovery.csv",
                        b"trading_date,close\n2026-01-01,20\n2026-01-02,21\n2026-01-03,22\n",
                        "text/csv",
                    )
                },
                data={
                    "metadata_json": json.dumps({**metadata, "instrument_id": second_listing["id"]})
                },
                headers={"Idempotency-Key": str(uuid4())},
            )
            if response.status_code != 201:
                raise RuntimeError("Synthetic silver recovery import failed")

        checked("Synthetic schema and all domain entities seeded")

        def snapshot(name):
            tables = {}
            with psycopg.connect(dbname=name, **credentials) as conn:
                for table in TABLES:
                    rows = conn.execute(
                        sql.SQL(
                            "SELECT row_to_json(t)::text FROM public.{} t ORDER BY row_to_json(t)::text"
                        ).format(sql.Identifier(table))
                    ).fetchall()
                    tables[table] = {"rows": len(rows), "sha256": fingerprint(rows)}
                constraints = conn.execute("""SELECT c.relname, conname, pg_get_constraintdef(k.oid)
                    FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid
                    JOIN pg_namespace n ON n.oid=c.relnamespace
                    WHERE n.nspname='public' ORDER BY 1,2""").fetchall()
                constraints = [normalized_constraint(*row) for row in constraints]
                indexes = conn.execute("""SELECT tablename,indexname,indexdef FROM pg_indexes
                    WHERE schemaname='public' ORDER BY 1,2""").fetchall()
                triggers = conn.execute("""SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid)
                    FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
                    JOIN pg_namespace n ON n.oid=c.relnamespace
                    WHERE n.nspname='public' AND NOT t.tgisinternal ORDER BY 1,2""").fetchall()
                functions = conn.execute("""SELECT proname,pg_get_functiondef(p.oid)
                    FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
                    WHERE n.nspname='public' ORDER BY 1""").fetchall()
                orphans = conn.execute("""SELECT count(*) FROM price_observations p
                    LEFT JOIN import_batches b ON b.id=p.batch_id
                    LEFT JOIN import_rows r ON r.batch_id=p.batch_id AND r.row_number=p.row_number
                    WHERE b.id IS NULL OR r.batch_id IS NULL""").fetchone()[0]
                if orphans:
                    raise RuntimeError("Broken observation provenance")
            return {
                "tables": tables,
                "schema_sha256": fingerprint([constraints, indexes, triggers, functions]),
                "orphan_observations": orphans,
            }

        def stable_payload(value):
            if isinstance(value, dict):
                return {
                    key: stable_payload(item)
                    for key, item in value.items()
                    if key not in {"request_id", "served_at", "computed_at"}
                }
            if isinstance(value, list):
                return [stable_payload(item) for item in value]
            return value

        def known_query(name):
            with client_for(name) as client:
                params = {
                    "source_id": provider["id"],
                    "basis": "RAW_CLOSE",
                    "assessment_as_of": "2026-01-03T00:00:00Z",
                }
                base = "/api/v1/instruments/" + listing["id"]
                payloads = {}
                for endpoint in ("history", "chart", "SMA", "EMA", "RSI"):
                    url = base + (
                        "/indicators" if endpoint in {"SMA", "EMA", "RSI"} else "/" + endpoint
                    )
                    query = {
                        **params,
                        **(
                            {"indicator": endpoint, "n": 2}
                            if endpoint in {"SMA", "EMA", "RSI"}
                            else {}
                        ),
                    }
                    response = client.get(url, params=query)
                    if response.status_code != 200:
                        raise RuntimeError("Known research query failed")
                    payload = response.json()
                    if endpoint == "history" and payload["data"][0]["close"] != "10.1234567890":
                        raise RuntimeError("Exact-price query mismatch")
                    if endpoint in {"SMA", "EMA", "RSI"} and not any(
                        v["value"] is not None for v in payload["data"]["values"]
                    ):
                        raise RuntimeError("Recovery indicator fixture is not seeded")
                    payloads[endpoint] = stable_payload(payload)
                response = client.post(
                    "/api/v1/comparisons",
                    json={
                        "series": [
                            {
                                "instrument_id": item["id"],
                                "source_id": provider["id"],
                                "price_basis": "RAW_CLOSE",
                            }
                            for item in (listing, second_listing)
                        ],
                        "start": "2026-01-01",
                        "end": "2026-01-03",
                        "assessment_as_of": "2026-01-03T00:00:00Z",
                    },
                )
                if response.status_code != 200 or response.json()["data"]["status"] != "AVAILABLE":
                    raise RuntimeError("Known recovery comparison failed")
                payloads["comparison"] = stable_payload(response.json())
                return fingerprint(payloads)

        before, before_query = snapshot(source), known_query(source)
        report.update(source=before, known_source_query_sha256=before_query)
        if not all(info["rows"] > 0 for info in before["tables"].values()):
            raise RuntimeError("Recovery fixture must populate every table")
        folder = ROOT / "backups" / ("recovery-" + run_id)
        folder.mkdir(parents=True, exist_ok=False)
        if os.name == "nt":
            identity = subprocess.run(
                ["whoami", "/user", "/fo", "csv", "/nh"], capture_output=True, text=True, check=True
            ).stdout
            sid = next(csv.reader(io.StringIO(identity.strip())))[1]
            subprocess.run(
                [
                    "icacls",
                    str(folder),
                    "/inheritance:r",
                    "/grant:r",
                    "*" + sid + ":(OI)(CI)F",
                    "*S-1-5-18:(OI)(CI)F",
                ],
                capture_output=True,
                check=True,
            )
        else:
            folder.chmod(0o700)
        archive = compose(
            "exec",
            "-T",
            "test-db",
            "pg_dump",
            "-U",
            credentials["user"],
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            source,
        )
        backup = folder / "synthetic.dump"
        with backup.open("xb") as handle:
            handle.write(archive)
        backup.chmod(0o600)
        digest = hashlib.sha256(archive).hexdigest()
        if hashlib.sha256(backup.read_bytes()).hexdigest() != digest:
            raise RuntimeError("Backup checksum mismatch")
        (folder / "synthetic.dump.sha256").write_text(digest + "  synthetic.dump\n")
        report.update(
            backup_path=backup.relative_to(ROOT).as_posix(),
            backup_sha256=digest,
            backup_bytes=len(archive),
        )
        checked("Binary backup created in restricted ignored directory; SHA-256 verified")
        toc = compose("exec", "-T", "test-db", "pg_restore", "--list", data=archive).decode()
        if not all("TABLE public " + table + " " in toc for table in TABLES):
            raise RuntimeError("Backup table-of-contents incomplete")
        checked("pg_restore archive integrity and table-of-contents inspection")
        with psycopg.connect(dbname="bullion_test", autocommit=True, **credentials) as admin:
            admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target)))
        compose(
            "exec",
            "-T",
            "test-db",
            "pg_restore",
            "-U",
            credentials["user"],
            "--dbname",
            target,
            "--no-owner",
            "--no-privileges",
            "--exit-on-error",
            "--single-transaction",
            data=backup.read_bytes(),
        )
        checked("Archive restored into newly created separate empty test database")
        after, after_query = snapshot(target), known_query(target)
        report.update(restored=after, known_restored_query_sha256=after_query)
        if before != after or before_query != after_query:
            raise RuntimeError("Restored data/schema/query differs from source")
        checked(
            "All table counts/hashes, schema objects, provenance and history/chart/indicator/comparison queries match"
        )
        try:
            with psycopg.connect(dbname=target, **credentials) as conn:
                conn.execute("UPDATE price_observations SET close=close")
        except psycopg.errors.RaiseException:
            checked("Restored append-only audit trigger rejects observation update")
        else:
            raise RuntimeError("Restored audit guard missing")
        report.update(
            success=True,
            source=before,
            restored=after,
            known_research_sha256=before_query,
            research_endpoints_verified=[
                "history",
                "chart",
                "SMA(2)",
                "EMA(2)",
                "RSI(2)",
                "price-only comparison",
            ],
            limitations=[
                "SYNTHETIC_TEST only; no application data or failover exercised",
                "Owner-data restore/cutover and retention policy not exercised",
            ],
        )
    except Exception as exc:
        report["failure_type"] = type(exc).__name__
        print("Recovery verification failed: " + type(exc).__name__, flush=True)
    finally:
        (artifacts / "recovery-verification.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if report["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
