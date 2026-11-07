"""Local lifecycle safety without changing active containers or using real data."""
import importlib.util
import json
from pathlib import Path
import subprocess
import pytest


@pytest.fixture
def manager(monkeypatch, tmp_path):
    path = Path(__file__).resolve().parents[2] / "scripts/local/manage.py"
    spec = importlib.util.spec_from_file_location("mvp_manager_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    (tmp_path / ".env").write_text("LOCAL_APP_TOKEN=synthetic-only\n")
    monkeypatch.setattr(module, "configuration", lambda: {"LOCAL_APP_TOKEN": "synthetic-only"})
    monkeypatch.setattr(module, "verify_ports", lambda _: None)
    module._test_preflight = module.preflight
    monkeypatch.setattr(module, "preflight", lambda _: None)
    monkeypatch.setattr(module, "status", lambda: {n: {"state": "running", "health": "healthy"} for n in module.SERVICES})
    return module


def test_stop_never_removes_or_resets_volumes(manager, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(manager, "compose", lambda *a: calls.append(a))
    assert manager.main(["stop"]) == 0
    assert calls == [("stop", "--timeout", "20", "ui", "api", "db")]
    assert "volume retained" in capsys.readouterr().out


def test_api_restart_handoff_stays_in_memory_and_never_retrieves_provider(manager, monkeypatch):
    calls, requests = [], []
    full = {"daily": {"series": [{"isin": "SYNTHETIC", "rows": [{"close": "123.0000000001"}]}]}, "quotes": [], "candles": []}
    empty = {"daily": {"series": [{"isin": "SYNTHETIC", "rows": []}]}, "quotes": [], "candles": []}
    state = [full, empty, full]
    def api(values, path, payload=None):
        requests.append((path, payload is not None))
        return {} if payload is not None else state.pop(0)
    monkeypatch.setattr(manager, "api", api)
    monkeypatch.setattr(manager, "compose", lambda *a: calls.append(a))
    assert manager.main(["restart", "--service", "api"]) == 0
    assert requests == [("/market-data/cache-transfer", False), ("/market-data/cache-transfer", False), ("/market-data/cache-transfer", True), ("/market-data/cache-transfer", False)]
    assert all("ensure" not in p for p, _ in requests)
    assert list(manager.ROOT.iterdir()) == [manager.ROOT / ".env"]
    assert all("db" not in call and "-v" not in call for call in calls)


def test_restart_refuses_to_overwrite_concurrent_cache(manager, monkeypatch, capsys):
    before = {"daily": {"series": []}, "quotes": [{"value": "synthetic-before"}], "candles": []}
    after = {**before, "quotes": [{"value": "synthetic-concurrent"}]}
    values = iter([before, after])
    monkeypatch.setattr(manager, "api", lambda *a: next(values))
    monkeypatch.setattr(manager, "compose", lambda *a: None)
    assert manager.main(["restart", "--service", "api"]) == 1
    assert "refusing to overwrite" in capsys.readouterr().out


def test_command_failure_never_exposes_raw_output(manager, monkeypatch):
    monkeypatch.setattr(manager.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess([], 1, b"sensitive", b"credential"))
    with pytest.raises(manager.LocalError, match="Sensitive output withheld"):
        manager.run(["synthetic"])


def test_status_reports_only_service_state_and_health(manager, monkeypatch):
    # Restore the real function from a fresh module to exercise JSON-lines parsing.
    source = Path(__file__).resolve().parents[2] / "scripts/local/manage.py"
    spec = importlib.util.spec_from_file_location("mvp_status_test", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "compose", lambda *a: (json.dumps({"Service": "api", "State": "running", "Health": "healthy", "Command": "not-exposed"}) + "\n").encode())
    result = module.status()
    assert result["api"] == {"state": "running", "health": "healthy"}
    assert "not-exposed" not in str(result)


def test_recovery_normalizes_only_exact_equivalent_provider_kind_enum_deparses():
    path = Path(__file__).resolve().parents[2] / "scripts/verify_recovery.py"
    spec = importlib.util.spec_from_file_location("mvp_recovery_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = "CHECK (((source_kind)::text = ANY ((ARRAY['USER_CSV'::character varying, 'DHANHQ'::character varying])::text[])))"
    restored = "CHECK (((source_kind)::text = ANY (ARRAY[('USER_CSV'::character varying)::text, ('DHANHQ'::character varying)::text])))"
    assert module.normalized_constraint("data_sources", "ck_source_kind", original) == module.normalized_constraint("data_sources", "ck_source_kind", restored)
    changed = restored.replace("'DHANHQ'", "'UNAPPROVED'")
    assert module.normalized_constraint("data_sources", "ck_source_kind", changed)[2] == changed
    assert module.normalized_constraint("other_table", "ck_source_kind", restored)[2] == restored


def test_populated_handoff_uses_origin_and_preserves_daily_quotes_intraday_and_budget(manager, monkeypatch):
    import io
    from contextlib import nullcontext
    from fastapi.testclient import TestClient
    from app.market_cache_transfer import export_cache
    from .test_market_session import setup
    from .provider_fixtures import collected
    from .conftest import TOKEN
    old, service, _, _ = setup()
    plan, result, _ = collected()
    old.state.transient_research.install(result, plan, names={x.symbol: "SYNTHETIC TEST ONLY" for x in service.provider.listings()}, data_class="SYNTHETIC_TEST")
    service.get_quotes()
    service.intraday(service.daily.store.listings()[0].id, 5, "previous")
    # Explicitly different daily vs cumulative counts; never infer one from the other.
    service.quote_attempts = 15
    service.budget.attempts = 2
    exported = export_cache(old)
    assert manager._test_preflight(exported)["daily_observations"] > 0
    fresh, target, _, _ = setup()
    with TestClient(fresh) as client:
        def urlopen(request, timeout):
            assert timeout == 20 and request.get_header("Origin") == "http://127.0.0.1:5173"
            assert request.full_url == "http://127.0.0.1:8000/api/v1/market-data/cache-transfer"
            response = client.post("/api/v1/market-data/cache-transfer", content=request.data, headers=dict(request.header_items()))
            assert response.status_code == 200
            return nullcontext(io.BytesIO(response.content))
        monkeypatch.setattr(manager.urllib.request, "urlopen", urlopen)
        restored = manager.api({"LOCAL_APP_TOKEN": TOKEN}, "/market-data/cache-transfer", exported)
    assert restored["daily_observations"] > 0 and restored["quotes"] == 4 and restored["intraday_candles"] == 75
    assert target.budget.attempts == 2 and target.quote_attempts == 15
    assert target.budget.day == service.budget.day
    assert target.quotes == service.quotes and target.candles == service.candles


def test_failed_preflight_stops_before_any_container_mutation(manager, monkeypatch):
    monkeypatch.setattr(manager, "api", lambda *a: {})
    def bad(_):
        raise manager.LocalError("Cache preflight failed")
    monkeypatch.setattr(manager, "preflight", bad)
    calls = []
    monkeypatch.setattr(manager, "compose", lambda *a: calls.append(a))
    assert manager.main(["restart", "--service", "api"]) == 1
    assert not calls


def test_previous_budget_day_is_explicit_and_not_reported_as_today():
    from datetime import timedelta
    from .test_market_session import setup
    _, service, _, _ = setup()
    service.budget.attempts = 24
    service.budget.day = service.budget.clock().date() - timedelta(days=1)
    assert service.policy()["provider_requests_today"] == 0
    assert service.policy()["provider_budget_day"] == service.budget.day
