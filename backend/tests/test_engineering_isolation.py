"""Engineering isolation must fail before any state-changing command."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location(
    "engineering_test", Path(__file__).resolve().parents[2] / "scripts/engineering.py"
)
engineering = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engineering)


def config():
    services = {
        name: {
            "image": "bullion-mvp05-"
            + ("ui" if name == "ui" else "db" if name in {"db", "test-db"} else "api")
            + ":engineering",
            "environment": {},
        }
        for name in ["db", "test-db", "api", "migrate", "ui"]
    }
    for name, port in {"api": 18000, "ui": 15173, "test-db": 15433}.items():
        services[name]["ports"] = [{"host_ip": "127.0.0.1", "published": str(port)}]
    for name in ["api", "migrate"]:
        services[name]["environment"]["DATABASE_URL"] = (
            "postgresql+psycopg://engineering:synthetic-engineering-only@db:5432/bullion_engineering"
        )
        services[name]["environment"]["LOCAL_APP_TOKEN"] = engineering.SYNTHETIC["LOCAL_APP_TOKEN"]
    return {
        "name": "bullion-mvp05",
        "services": services,
        "volumes": {"bullion_data": {"name": "bullion-mvp05_bullion_data"}},
        "networks": {"default": {"name": "bullion-mvp05_default"}},
    }


def test_isolated_configuration_is_accepted():
    engineering.validate_config(config())


@pytest.mark.parametrize(
    "defect",
    [
        "project",
        "port",
        "public",
        "volume",
        "network",
        "credentials",
        "provider_enabled",
        "bind_mount",
        "image",
        "host_network",
    ],
)
def test_shared_or_live_configuration_rejected(defect):
    c = deepcopy(config())
    if defect == "project":
        c["name"] = "bullion-vs01"
    elif defect == "port":
        c["services"]["ui"]["ports"][0]["published"] = "5173"
    elif defect == "public":
        c["services"]["ui"]["ports"][0]["host_ip"] = "0.0.0.0"
    elif defect == "volume":
        c["volumes"]["bullion_data"]["name"] = "bullion-vs01_bullion_data"
    elif defect == "network":
        c["networks"]["default"]["external"] = True
    elif defect == "credentials":
        c["services"]["api"]["environment"]["DHAN_ACCESS_TOKEN"] = "not-allowed-even-if-synthetic"
    elif defect == "provider_enabled":
        c["services"]["api"]["environment"]["MARKET_DATA_ENABLED"] = "true"
    elif defect == "bind_mount":
        c["services"]["api"]["volumes"] = [{"type": "bind", "source": "owner-cache"}]
    elif defect == "image":
        c["services"]["api"]["image"] = "bullion-vs01-api:latest"
    elif defect == "host_network":
        c["services"]["api"]["network_mode"] = "host"
    with pytest.raises(engineering.IsolationError):
        engineering.validate_config(c)


@pytest.mark.parametrize("defect", ["volume_driver", "network_driver", "database_destination"])
def test_indirect_shared_state_rejected(defect):
    c = config()
    if defect == "volume_driver":
        c["volumes"]["bullion_data"]["driver_opts"] = {
            "type": "none",
            "o": "bind",
            "device": "owner-volume",
        }
    elif defect == "network_driver":
        c["networks"]["default"]["driver_opts"] = {
            "com.docker.network.bridge.name": "owner-network"
        }
    else:
        c["services"]["api"]["environment"]["DATABASE_URL"] = (
            "postgresql+psycopg://test:test@host.docker.internal:5432/owner"
        )
    with pytest.raises(engineering.IsolationError):
        engineering.validate_config(c)


def test_wrong_settings_file_rejected_before_docker(monkeypatch, tmp_path):
    monkeypatch.setattr(engineering, "ROOT", tmp_path)
    (tmp_path / ".git").write_text("gitdir: synthetic-worktree")
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts/engineering.env").write_text("POSTGRES_USER=unapproved\n")

    def forbidden(*args, **kwargs):
        raise AssertionError("Docker must not be called")

    monkeypatch.setattr(engineering.subprocess, "run", forbidden)
    with pytest.raises(engineering.IsolationError, match="settings file"):
        engineering.validate()
