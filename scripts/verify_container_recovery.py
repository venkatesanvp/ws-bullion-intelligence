"""MVP06 isolated synthetic container recovery; never controls the owner project."""

import pathlib
import json
import subprocess
import time
import urllib.request

import engineering as eng

R = pathlib.Path(__file__).resolve().parents[1]

eng.validate()
env = eng.environment()
prefix = eng.prefix()
receipts = []


def compose(*args):
    p = subprocess.run(prefix + list(args), cwd=R, env=env, capture_output=True, timeout=150)
    if p.returncode:
        raise RuntimeError("Engineering Compose operation failed; raw output withheld")
    return p.stdout.decode()


def api(path, payload=None):
    req = urllib.request.Request(
        "http://127.0.0.1:18010/api/v1" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": "Bearer " + eng.SYNTHETIC["LOCAL_APP_TOKEN"],
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:15183",
        },
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.load(resp)["data"]


def ready():
    limit = time.monotonic() + 90
    while time.monotonic() < limit:
        try:
            api("/health/ready")
            with urllib.request.urlopen("http://127.0.0.1:15183/_health", timeout=3) as r:
                assert r.status == 200
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Engineering readiness timed out")


def sql(q):
    return compose(
        "exec", "-T", "db", "psql", "-At", "-U", "engineering", "-d", "bullion_engineering", "-c", q
    ).strip()


api(
    "/instruments",
    {
        "exchange": "XNSE",
        "symbol": "MVP06_SYNTH_" + str(time.time_ns())[-8:],
        "name": "SYNTHETIC TEST RECOVERY MARKER NOT A REAL ETF",
        "metal": "GOLD",
        "currency": "INR",
    },
)
query = (
    "SELECT md5(coalesce(string_agg(row_to_json(t)::text, ',' ORDER BY id),'')) FROM instruments t"
)
before = sql(query)
for services in [("api",), ("ui",), ("db",), ("db", "api", "ui")]:
    t = time.monotonic()
    compose("restart", "--timeout", "20", *services)
    ready()
    assert sql(query) == before
    assert api("/market-data/session-policy")["provider_requests_today"] == 0
    receipts.append(
        {
            "operation": "restart",
            "services": services,
            "milliseconds": round((time.monotonic() - t) * 1000),
            "catalog_checksum_preserved": True,
            "provider_attempts": 0,
        }
    )
t = time.monotonic()
compose("stop", "--timeout", "20", "ui", "api", "db")
exits = json.loads(
    subprocess.check_output(
        [eng.DOCKER, "inspect", *["bullion-mvp06-" + s + "-1" for s in ["api", "ui", "db"]]]
    )
)
api_logs = subprocess.check_output(
    [eng.DOCKER, "logs", "--tail", "20", "bullion-mvp06-api-1"], stderr=subprocess.STDOUT
).decode()
assert exits[0]["State"]["ExitCode"] in {0, 143} and "Application shutdown complete." in api_logs
assert all(x["State"]["ExitCode"] == 0 for x in exits[1:])
assert not any(x["State"]["OOMKilled"] for x in exits)
compose("up", "-d", "--no-build", "--wait", "db", "api", "ui")
ready()
assert sql(query) == before
receipts.append(
    {
        "operation": "stop/start",
        "milliseconds": round((time.monotonic() - t) * 1000),
        "graceful_exit_codes": [x["State"]["ExitCode"] for x in exits],
        "catalog_checksum_preserved": True,
    }
)
ids = compose("ps", "-q", "api", "ui", "db").splitlines()
beforestarts = json.loads(subprocess.check_output([eng.DOCKER, "inspect", *ids]))
compose("up", "-d", "--no-build", "--no-recreate", "--wait", "db", "api", "ui")
afterstarts = json.loads(subprocess.check_output([eng.DOCKER, "inspect", *ids]))
assert [x["State"]["StartedAt"] for x in beforestarts] == [
    x["State"]["StartedAt"] for x in afterstarts
]
users = {s: compose("exec", "-T", s, "id", "-u").strip() for s in ["api", "ui", "db"]}
assert all(v != "0" for v in users.values())
assert compose("exec", "-T", "db", "sh", "-c", "test ! -e /usr/local/bin/gosu") == ""
flags = api("/market-data/session-policy")
assert not flags["enabled"] and not flags["quotes_enabled"] and not flags["intraday_enabled"]
result = {
    "data_class": "SYNTHETIC_TEST",
    "project": eng.PROJECT,
    "operations": receipts,
    "idempotent_up_no_recreate": True,
    "runtime_uids": users,
    "gosu_absent": True,
    "catalog_sha": before,
    "scope": "Container restart preserves synthetic SQL catalogue; populated RAM handoff/failure tests run separately at HTTP boundary. Direct unguarded API restart loses RAM by design; no durable cache claim.",
}
(R / "artifacts/mvp06-container-recovery.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
