"""MVP-02/03 display metadata must use exactly the eligible forecast observations."""
import json
import logging
from types import SimpleNamespace
import pytest
from app.forecast_market_adapter import adapt
from app.provider_budget import ProviderBudget
from .forecast_research_fixtures import service_fixture


@pytest.mark.parametrize("index", range(4))
def test_chart_history_matches_forecast_observations_without_loss_of_precision(index):
    service, reader, _, _, clock, _, cal = service_fixture(index=index)
    i, s, rows = reader()
    view = adapt(i, s, rows, listings=service.market.provider.listings(), now=clock[0], calendar_override=cal)
    assert len(view.metadata["history"]) == 120
    for actual, expected in zip(view.metadata["history"], view.dataset.observations[-120:]):
        assert actual == {"time": str(expected.session_date), **{key: format(getattr(expected, key), "f") for key in ["open", "high", "low", "close"]}, "volume": str(expected.volume)}


def test_provider_audit_contains_only_operation_and_counts_not_response_or_error_text(caplog):
    budget = ProviderBudget(pause=lambda _: None)
    result = SimpleNamespace(request_attempts=1, failure=None, secret="never-log-me", response="restricted-prices")
    with caplog.at_level(logging.INFO, logger="bullion"):
        assert budget.invoke(lambda: result, operation="DAILY_HISTORY") is result
    event = json.loads(caplog.records[-1].message)
    assert {k: event[k] for k in ("event", "operation", "request_attempts", "counter_before", "counter_after", "failed")} == {"event": "PROVIDER_OPERATION_COMPLETED", "operation": "DAILY_HISTORY", "request_attempts": 1, "counter_before": 0, "counter_after": 1, "failed": False}
    assert "never-log-me" not in caplog.text and "restricted-prices" not in caplog.text
    with pytest.raises(ValueError):
        budget.invoke(lambda: result, operation="secret-not-allowed")
