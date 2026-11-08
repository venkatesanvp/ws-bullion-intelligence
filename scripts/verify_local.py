"""Run authorized VS-01 checks; database cleanup is limited to the disposable test service."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "synthetic-test-token-not-a-real-secret-000000"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database",
        action="store_true",
        help="Start isolated Compose test-db and run PostgreSQL tests",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Run real-backend Chromium workflow; requires --database and free ports 15184/18011/18012",
    )
    parser.add_argument(
        "--engineering",
        action="store_true",
        help="Synthetic MVP06 Compose project; never uses UAT env, ports or volumes",
    )
    args = parser.parse_args()
    if args.browser and not args.database:
        parser.error("--browser requires --database; no production database fallback")
    os.chdir(ROOT)
    if args.engineering:
        from engineering import validate

        validate()
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm") or (
        "C:/Program Files/nodejs/npm.cmd" if os.name == "nt" else None
    )
    if not python.exists() or not npm:
        parser.error("Run uv sync and npm ci in frontend first")
    env = os.environ.copy()
    env["LOCAL_APP_TOKEN"] = TOKEN
    env["DATABASE_URL"] = "postgresql+psycopg://test:test@127.0.0.1:1/unavailable_test"
    records = []

    def run(name, command, cwd=ROOT, timeout=600):
        print("CHECK:", name, flush=True)
        try:
            command = [str(x) for x in command]
            if os.name == "nt" and command[0].lower().endswith("npm.cmd"):
                npm_dir = Path(command[0]).parent
                command = [
                    str(npm_dir / "node.exe"),
                    str(npm_dir / "node_modules/npm/bin/npm-cli.js"),
                    *command[1:],
                ]
            result = subprocess.run(command, cwd=cwd, env=env, timeout=timeout, check=False)
            code = result.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(name + " could not run: " + type(exc).__name__, flush=True)
            code = 1
        records.append({"check": name, "exit_code": code})
        return code == 0

    database_ready = False
    if args.database:
        docker = shutil.which("docker") or (
            "C:/Program Files/Docker/Docker/resources/bin/docker.exe"
            if os.name == "nt"
            else "docker"
        )
        # Only generated key=value settings are read. Nothing is printed or passed in command-line arguments.
        local_file = ROOT / ("artifacts/engineering.env" if args.engineering else ".env")
        if not local_file.exists():
            parser.error("Run scripts/configure_local.py before isolated database tests")
        local = dict(
            line.split("=", 1)
            for line in local_file.read_text(encoding="utf-8").splitlines()
            if "=" in line and not line.startswith("#")
        )
        if not all(local.get(k) for k in ["POSTGRES_USER", "POSTGRES_PASSWORD"]):
            parser.error("Local PostgreSQL configuration is incomplete")
        env.update({k: local[k] for k in ["POSTGRES_USER", "POSTGRES_PASSWORD"]})
        env["POSTGRES_DB"] = local.get("POSTGRES_DB", "bullion")
        database_ready = run(
            "isolated PostgreSQL startup",
            [
                docker,
                "compose",
                *(
                    [
                        "--project-name",
                        "bullion-mvp06",
                        "--file",
                        "compose.engineering.yaml",
                        "--env-file",
                        "artifacts/engineering.env",
                    ]
                    if args.engineering
                    else []
                ),
                "--profile",
                "test",
                "up",
                "-d",
                "--wait",
                "test-db",
            ],
            timeout=180,
        )
        if database_ready:
            user = quote(local["POSTGRES_USER"], safe="")
            password = quote(local["POSTGRES_PASSWORD"], safe="")
            env["TEST_DATABASE_URL"] = (
                f"postgresql+psycopg://{user}:{password}@127.0.0.1:{15443 if args.engineering else 55433}/bullion_test"
            )
            env["DATABASE_URL"] = env["TEST_DATABASE_URL"]
            env["TEST_APP_TOKEN"] = TOKEN

    run("Python lint", [python, "-m", "ruff", "check", "backend", "scripts"])
    backend = [python, "-m", "pytest", "-q", "--junitxml=artifacts/backend-tests.xml"]
    if not database_ready:
        backend += ["backend/tests/test_csv.py", "backend/tests/test_access.py"]
    backend_ok = run(
        "backend + PostgreSQL" if database_ready else "backend without PostgreSQL", backend
    )
    run("frontend components", [npm, "test"], ROOT / "frontend")
    run("frontend production build", [npm, "run", "build"], ROOT / "frontend")
    if args.browser and database_ready and backend_ok:
        run("real-backend browser workflow", [npm, "run", "test:e2e"], ROOT / "frontend")
    elif args.browser:
        records.append({"check": "real-backend browser workflow not executed", "exit_code": 1})
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "database_requested": args.database,
        "database_ready": database_ready,
        "browser_requested": args.browser,
        "checks": records,
        "limitations": []
        if database_ready
        else ["PostgreSQL migration/integrity/concurrency/runtime checks not executed"],
    }
    (artifacts / "verification.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return (
        1 if any(r["exit_code"] for r in records) or (args.database and not database_ready) else 0
    )


if __name__ == "__main__":
    sys.exit(main())
