"""MVP05 synthetic engineering lifecycle; refuses owner env/shared runtime configuration."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "bullion-mvp05"
DOCKER = shutil.which("docker") or "C:/Program Files/Docker/Docker/resources/bin/docker.exe"
SYNTHETIC = {
    "POSTGRES_USER": "engineering",
    "POSTGRES_PASSWORD": "synthetic-engineering-only",
    "POSTGRES_DB": "bullion_engineering",
    "LOCAL_APP_TOKEN": "synthetic-engineering-token-not-a-secret-000000",
}


class IsolationError(Exception):
    pass


def environment():
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("DHAN_", "MARKET_")) and k not in {"DATABASE_URL", "TEST_DATABASE_URL"}
    }
    env.update(SYNTHETIC)
    return env


def prefix():
    return [
        DOCKER,
        "compose",
        "--project-name",
        PROJECT,
        "--file",
        "compose.engineering.yaml",
        "--env-file",
        "artifacts/engineering.env",
    ]


def validate_config(config):
    if config.get("name") != PROJECT:
        raise IsolationError("Unexpected engineering project")
    services = config["services"]
    expected = {"api": 18000, "ui": 15173, "test-db": 15433}
    if set(services) != {"db", "migrate", "api", "ui", "test-db"}:
        raise IsolationError("Unexpected engineering services")
    for name, service in services.items():
        if (
            service.get("privileged")
            or service.get("network_mode")
            or service.get("container_name")
        ):
            raise IsolationError("Shared/privileged runtime rejected")
        if not service.get("image", "").startswith("bullion-mvp05-"):
            raise IsolationError("Engineering image name required")
        for port in service.get("ports", []):
            if port.get("host_ip") != "127.0.0.1" or str(port.get("published")) != str(
                expected.get(name)
            ):
                raise IsolationError("Unexpected public or shared port")
        for mount in service.get("volumes", []):
            if mount.get("type") != "volume" or mount.get("source") != "bullion_data":
                raise IsolationError("Shared/bind mount rejected")
        env = service.get("environment", {})
        if (
            name in {"api", "migrate"}
            and env.get("DATABASE_URL")
            != "postgresql+psycopg://engineering:synthetic-engineering-only@db:5432/bullion_engineering"
        ):
            raise IsolationError("Engineering database destination required")
        for key, value in env.items():
            if (
                key.startswith("DHAN_")
                and key not in {"DHAN_API_BASE_URL", "DHAN_DATA_API_ENABLED"}
                and value
            ):
                raise IsolationError("Provider credentials forbidden in engineering")
            if (
                key
                in {
                    "DHAN_DATA_API_ENABLED",
                    "MARKET_DATA_ENABLED",
                    "MARKET_QUOTES_ENABLED",
                    "MARKET_INTRADAY_ENABLED",
                    "MARKET_STREAM_ENABLED",
                }
                and str(value).lower() != "false"
            ):
                raise IsolationError("Live provider flags forbidden in engineering")
        if (
            name in {"api", "migrate"}
            and env.get("LOCAL_APP_TOKEN") != SYNTHETIC["LOCAL_APP_TOKEN"]
        ):
            raise IsolationError("Synthetic app token required")
    for key, value in config.get("volumes", {}).items():
        if (
            value.get("external")
            or value.get("driver_opts")
            or value.get("name") != PROJECT + "_" + key
        ):
            raise IsolationError("Shared external volume rejected")
    for key, value in config.get("networks", {}).items():
        if (
            value.get("external")
            or value.get("driver_opts")
            or value.get("name") != PROJECT + "_" + key
        ):
            raise IsolationError("Shared external network rejected")


def validate():
    if not (ROOT / ".git").is_file() or (ROOT / ".env").exists():
        raise IsolationError("Use a separate Git worktree without an owner .env")
    expected = "".join(k + "=" + v + "\n" for k, v in SYNTHETIC.items())
    path = ROOT / "artifacts/engineering.env"
    if not path.is_file() or path.read_text() != expected:
        raise IsolationError("Synthetic settings file mismatch")
    config = subprocess.run(
        prefix() + ["--profile", "test", "config", "--format", "json"],
        cwd=ROOT,
        env=environment(),
        capture_output=True,
        timeout=30,
    )
    if config.returncode:
        raise IsolationError("Engineering configuration rejected; values withheld")
    validate_config(json.loads(config.stdout))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["setup", "status", "build", "start", "stop", "restart", "test", "recover"],
    )
    parser.add_argument("--service", choices=["db", "api", "ui"])
    args = parser.parse_args()
    try:
        if args.action == "setup":
            if not (ROOT / ".git").is_file() or (ROOT / ".env").exists():
                raise IsolationError("Separate worktree without owner .env required")
            (ROOT / "artifacts").mkdir(exist_ok=True)
            path = ROOT / "artifacts/engineering.env"
            expected = "".join(k + "=" + v + "\n" for k, v in SYNTHETIC.items())
            if path.exists() and path.read_text() != expected:
                raise IsolationError("Existing engineering settings differ; refusing overwrite")
            if not path.exists():
                path.write_text(expected)
        validate()
        commands = {
            "setup": [],
            "status": ["ps", "--all"],
            "build": ["build", "db", "api", "ui"],
            "start": ["--profile", "test", "up", "-d", "--no-build", "--wait"],
            "stop": ["--profile", "test", "stop", "--timeout", "20"],
            "restart": [
                "restart",
                "--timeout",
                "20",
                *([args.service] if args.service else ["db", "api", "ui"]),
            ],
        }
        if args.action in {"test", "recover"}:
            command = [
                sys.executable,
                "scripts/verify_recovery.py"
                if args.action == "recover"
                else "scripts/verify_local.py",
                "--engineering",
            ]
            if args.action == "test":
                command += ["--database", "--browser"]
        else:
            command = prefix() + commands[args.action] if commands[args.action] else None
        if command:
            return subprocess.run(command, cwd=ROOT, env=environment(), timeout=1800).returncode
        print("PASS: isolated engineering configuration; synthetic credentials; provider disabled")
        return 0
    except (IsolationError, subprocess.TimeoutExpired):
        print("FAIL: engineering isolation validation failed; no runtime action taken")
        return 1


if __name__ == "__main__":
    sys.exit(main())
