"""MVP06 built-image UI smoke, synthetic fixture API, engineering-only ports."""

import subprocess
import time
import urllib.request
import pathlib
import engineering

r = pathlib.Path(__file__).resolve().parents[1]
engineering.validate()
env = engineering.environment()
env.update(
    DATABASE_URL="postgresql+psycopg://engineering:synthetic-engineering-only@127.0.0.1:15443/bullion_test",
    TEST_DATABASE_URL="postgresql+psycopg://engineering:synthetic-engineering-only@127.0.0.1:15443/bullion_test",
    LOCAL_APP_TOKEN="synthetic-test-token-not-a-real-secret-000000",
    ALLOWED_ORIGINS="http://127.0.0.1:15183",
    PYTHONPATH=str(r / "backend"),
)
with (r / "artifacts/production-fixture.log").open("w") as log:
    p = subprocess.Popen(
        [
            str(r / ".venv/Scripts/python.exe"),
            "-m",
            "uvicorn",
            "tests.session_browser_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "18012",
            "--no-access-log",
        ],
        cwd=r,
        env=env,
        stdout=log,
        stderr=log,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    try:
        for n in range(60):
            if p.poll() is not None:
                raise RuntimeError("Synthetic test app failed")
            try:
                with urllib.request.urlopen("http://127.0.0.1:18012/api/v1/health/live", timeout=2):
                    break
            except Exception:
                time.sleep(0.5)
        result = subprocess.run(
            ["C:/Program Files/nodejs/node.exe", "frontend/e2e/production-smoke.mjs"],
            cwd=r,
            timeout=120,
        )
        if result.returncode:
            raise RuntimeError("Production synthetic smoke failed")
    finally:
        p.terminate()
        p.wait(timeout=15)
