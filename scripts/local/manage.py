"""Windows/local Compose lifecycle. No secret output, provider retrieval or volume deletion."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[2]
DOCKER = shutil.which("docker") or "C:/Program Files/Docker/Docker/resources/bin/docker.exe"
SERVICES = ("db", "api", "ui")


class LocalError(Exception):
    pass


def run(command, timeout=240):
    try:
        p = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        raise LocalError(
            "Command unavailable or timed out; no configuration values logged."
        ) from None
    if p.returncode:
        raise LocalError("Local command failed; inspect service status. Sensitive output withheld.")
    return p.stdout


def compose(*args):
    return run([DOCKER, "compose", *args])


def configuration():
    if not (ROOT / ".env").is_file():
        raise LocalError(
            "Missing .env. Run scripts/configure_local.py manually; existing files are never overwritten."
        )
    from dotenv import dotenv_values

    values = dotenv_values(ROOT / ".env", interpolate=False)
    if any(not values.get(k) for k in ("POSTGRES_USER", "POSTGRES_PASSWORD", "LOCAL_APP_TOKEN")):
        raise LocalError("Required local database/application configuration is missing.")
    git = ["git", "-c", "safe.directory=" + ROOT.as_posix()]
    if run([*git, "ls-files", ".env"]).strip():
        raise LocalError(".env must not be tracked.")
    run([*git, "check-ignore", "-q", ".env"])
    run([DOCKER, "version", "--format", "{{.Server.Version}}"])
    compose("version", "--short")
    config = json.loads(compose("config", "--format", "json"))
    for name, service in config["services"].items():
        if service.get("privileged") or service.get("network_mode") == "host":
            raise LocalError("Privileged/host-network service is outside local MVP policy.")
        for port in service.get("ports", []):
            if port.get("host_ip") != "127.0.0.1":
                raise LocalError("Published ports must bind to loopback.")
        if name != "api" and any(k.startswith("DHAN_") for k in service.get("environment", {})):
            raise LocalError("Provider credentials must remain API-only.")
    for directory in ("artifacts", "backups"):
        (ROOT / directory).mkdir(exist_ok=True)
    return values


def api(values, path, payload=None):
    request = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": "Bearer " + values["LOCAL_APP_TOKEN"],
            "Content-Type": "application/json",
            **({"Origin": "http://127.0.0.1:5173"} if payload is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)["data"]
    except urllib.error.HTTPError as error:
        raise LocalError(
            "Local API operation rejected (HTTP "
            + str(error.code)
            + "); no response or credentials logged."
        ) from None
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError):
        raise LocalError("Local API operation failed; no response or credentials logged.") from None


def preflight(transfer):
    """Validate the complete candidate restore in a disposable in-process app first.

    No lifespan/startup, DB connection, network request, file write or credential copy.
    The original running process is left intact if this fails.
    """
    sys.path.insert(0, str(ROOT / "backend"))
    from app.config import Settings
    from app.main import create_app
    from app.market_cache_transfer import SessionTransfer, restore_cache

    shadow = create_app(
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://test:test@127.0.0.1:1/unavailable_test",
            local_app_token="synthetic-preflight-validation-not-a-secret-000000",
            market_data_enabled=True,
            market_quotes_enabled=False,
            market_intraday_enabled=False,
            market_stream_enabled=False,
        )
    )
    try:
        return restore_cache(shadow, SessionTransfer.model_validate(transfer))
    except Exception:
        raise LocalError("Cache preflight failed; active API has not been replaced.") from None
    finally:
        shadow.state.engine.dispose()


def status():
    rows = [
        json.loads(line)
        for line in compose("ps", "--all", "--format", "json").decode().splitlines()
        if line
    ]
    # Compose emits a JSON array on some versions and JSON lines on others.
    if len(rows) == 1 and isinstance(rows[0], list):
        rows = rows[0]
    result = {name: {"state": "absent", "health": "unknown"} for name in SERVICES}
    for row in rows:
        name = row.get("Service")
        if name in result:
            result[name] = {
                "state": row.get("State"),
                "health": row.get("Health") or "not-configured",
            }
    return result


def verify_ports(current):
    for port, service in ((5173, "ui"), (8000, "api")):
        if current[service]["state"] == "running":
            continue
        with socket.socket() as probe:
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                raise LocalError(
                    "Required local port " + str(port) + " is occupied by another process."
                ) from None


def fingerprint(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def has_cache(payload):
    return any(s["rows"] for s in payload["daily"]["series"]) or bool(
        payload["quotes"] or payload["candles"]
    )


def stable_transfer(payload):
    # Only transient catalogue IDs may change; all observation/provenance/budget
    # fields participate in the comparison.
    result = {k: v for k, v in payload.items() if k != "daily"}
    result["daily"] = sorted(
        (
            {k: v for k, v in series.items() if k not in {"instrument_id", "source_id"}}
            for series in payload["daily"]["series"]
        ),
        key=lambda item: item["isin"],
    )
    return result


def restore_transfer(values, transfer):
    after = api(values, "/market-data/cache-transfer")
    if fingerprint(stable_transfer(after)) == fingerprint(stable_transfer(transfer)):
        return
    if has_cache(after):
        raise LocalError("Replacement cache changed concurrently; refusing to overwrite it.")
    api(values, "/market-data/cache-transfer", transfer)
    restored = api(values, "/market-data/cache-transfer")
    if fingerprint(stable_transfer(restored)) != fingerprint(stable_transfer(transfer)):
        raise LocalError("RAM handoff verification failed.")


def interactive():
    return sys.stdin.isatty()


def hold_for_recovery(values, transfer):
    # Explicit operator retries only. Never write the payload to disk/SQL and
    # never exit on a failed restore while it is our only retained copy.
    while True:
        print(
            "RECOVERY REQUIRED: original payload retained in this process RAM. Keep this terminal open. Repair the local service separately; type retry to restore/verify, or DISCARD TRANSIENT CACHE to explicitly abandon it."
        )
        try:
            action = input().strip()
        except (EOFError, KeyboardInterrupt):
            time.sleep(1)
            continue
        if action == "DISCARD TRANSIENT CACHE":
            raise LocalError(
                "Operator explicitly discarded transient handoff; original provenance may be lost."
            )
        if action == "retry":
            try:
                restore_transfer(values, transfer)
                return
            except LocalError:
                print(
                    "Restore/verification still failed; RAM copy retained; no provider call made."
                )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["setup", "start", "stop", "restart", "status", "test", "recover"]
    )
    parser.add_argument("--service", choices=SERVICES, help="Optional restart target")
    args = parser.parse_args(argv)
    os.chdir(ROOT)
    try:
        values = configuration()
        original = hashlib.sha256((ROOT / ".env").read_bytes()).hexdigest()
        current = status()
        if args.action == "setup":
            verify_ports(current)
            print(
                "PASS: Docker, Compose, configuration, loopback ports and ignored local directories."
            )
        elif args.action in {"start", "restart"}:
            verify_ports(current)
            # This payload stays only in this process's RAM. No file/SQL/cache snapshot is created.
            transfer = None
            if current["api"]["state"] == "running" and (
                args.action == "start" or args.service in (None, "api")
            ):
                transfer = api(values, "/market-data/cache-transfer")
                preflight(transfer)
                print("PASS: complete RAM handoff preflight before replacing the active API.")
            if transfer is not None and not interactive():
                raise LocalError(
                    "Noninteractive populated/API restart refused before replacement; use an interactive terminal with the RAM recovery guard."
                )
            try:
                if args.action == "start":
                    compose("up", "-d", "--build", "--wait", "--wait-timeout", "120")
                else:
                    targets = [args.service] if args.service else list(SERVICES)
                    compose("restart", "--timeout", "20", *targets)
                    compose(
                        "up", "-d", "--no-recreate", "--wait", "--wait-timeout", "120", *targets
                    )
                if transfer is not None:
                    restore_transfer(values, transfer)
            except (LocalError, KeyboardInterrupt) as error:
                print(
                    "Recovery required after local operation failure; original RAM copy retained."
                )
                if isinstance(error, LocalError):
                    print(str(error))
                if transfer is None:
                    raise
                hold_for_recovery(values, transfer)
            if transfer is not None:
                print(
                    "PASS: transient cache/provenance/budget verified; no disk persistence. Forecast registries expire on restart."
                )
            print(json.dumps(status()))
            print("Local application: http://127.0.0.1:5173")
        elif args.action == "stop":
            compose("stop", "--timeout", "20", "ui", "api", "db")
            print(
                "Services stopped; database volume retained. Transient prices and forecasts are lost on stop."
            )
        elif args.action == "status":
            print(json.dumps(current))
        else:
            script = (
                "scripts/verify_recovery.py"
                if args.action == "recover"
                else "scripts/verify_local.py"
            )
            command = [sys.executable, script]
            if args.action == "test":
                command += ["--database", "--browser"]
            result = subprocess.run(command, cwd=ROOT, timeout=1800)
            if result.returncode:
                raise LocalError("Verification failed; inspect the sanitized test report.")
            print("PASS: " + args.action)
        if original != hashlib.sha256((ROOT / ".env").read_bytes()).hexdigest():
            raise LocalError("Environment file changed during operation.")
        return 0
    except (LocalError, subprocess.TimeoutExpired) as error:
        print(
            "FAIL: " + (str(error) if isinstance(error, LocalError) else "Verification timed out.")
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
