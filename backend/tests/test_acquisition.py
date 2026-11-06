"""Step 5D.2 orchestration tests. All prices, volumes, calendars and credentials synthetic."""

from datetime import date, timedelta
import json
import socket

import httpx
import pytest

from app.acquisition import collect_history, preflight, work_items
from app.dhan_import import main
from .provider_fixtures import TOKEN, body_for, collected, plan, provider_for


@pytest.fixture(autouse=True)
def no_live_network(monkeypatch):
    def deny(*a, **k):
        pytest.fail("Live connection forbidden")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def test_one_year_four_instruments_inclusive_exclusive_and_controls():
    p = plan()
    provider, calls = provider_for(p)
    waits = []
    pre = preflight(provider, p)
    assert not calls and pre["expected_requests"] == 4
    assert pre["requested_start"] == "2025-11-02" and pre["requested_end"] == "2026-11-02"
    result = collect_history(provider, p, request_approved=True, pause=waits.append)
    assert waits == [1.0] * 3 and len(calls) == result.attempted_requests == 4
    assert [json.loads(r.content)["securityId"] for r in calls] == [
        "21401",
        "21428",
        "14428",
        "8080",
    ]
    assert all(json.loads(r.content)["toDate"] == "2026-11-03" for r in calls)
    assert all(len(s.observations) == 261 for s in result.series)
    assert all(not s.missing_sessions for s in result.series)
    assert TOKEN not in json.dumps(result.safe_summary())
    assert '"close"' not in json.dumps(result.safe_summary())


@pytest.mark.parametrize("years", [3, 5])
def test_multi_year_partitioning_no_gaps_or_overlap(years):
    p = plan(start=date(2026 - years, 11, 2), max_requests=32)
    provider, _ = provider_for(p)
    items = work_items(provider, p)
    for listing in provider.listings():
        own = [x for x in items if x.listing == listing]
        assert own[0].start == p.start and own[-1].end == p.end
        assert all((x.end - x.start).days < 366 for x in own)
        assert all(b.start == a.end + timedelta(days=1) for a, b in zip(own, own[1:]))
    result = collect_history(provider, p, request_approved=True, pause=lambda _: None)
    assert result.status == "COLLECTED_UNQUALIFIED"
    assert result.attempted_requests == len(items)
    assert all(len(s.observations) == len(p.calendar.session_dates) for s in result.series)


def test_request_budget_checked_before_transport():
    p = plan(start=date(2023, 11, 2))
    provider, calls = provider_for(p)
    result = collect_history(provider, p, request_approved=True)
    assert result.failure_code == "INVALID_PLAN_OR_REQUEST_BUDGET" and not calls


def test_requires_explicit_approval():
    p = plan()
    provider, calls = provider_for(p)
    result = collect_history(provider, p)
    assert result.attempted_requests == 0 and not calls


def test_partial_responses_and_missing_sessions_no_fill():
    p = plan()
    absent = p.calendar.session_dates[100]
    _, result, _ = collected(p, missing=(absent,))
    for item in result.series:
        assert len(item.observations) == 260 and item.missing_sessions == (absent,)
        assert all(r.trading_date != absent for r in item.observations)


def test_calendar_holidays_and_special_weekend_sessions_are_explicit():
    p = plan()
    holiday = p.calendar.session_dates[20]
    p.calendar.session_dates.remove(holiday)
    special = date(2026, 1, 3)
    p.calendar.session_dates.append(special)
    _, result, _ = collected(p)
    assert all(special in {r.trading_date for r in x.observations} for x in result.series)
    assert all(holiday not in {r.trading_date for r in x.observations} for x in result.series)


def test_inception_coverage_not_fabricated():
    p = plan(
        availability={
            "INF277KA1976": {"inception_date": "2026-02-02", "evidence_ref": "SYNTHETIC inception"}
        }
    )
    _, result, calls = collected(p)
    tata = result.series[0]
    assert json.loads(calls[0].content)["fromDate"] == "2026-02-02"
    assert tata.unavailable_before_inception == (p.start, date(2026, 2, 1))
    assert all(r.trading_date >= date(2026, 2, 2) for r in tata.observations)
    assert len(tata.observations) < len(result.series[1].observations)


def test_entire_range_before_inception_has_no_request_for_that_listing():
    p = plan(
        availability={
            "INF277KA1976": {"inception_date": "2027-01-01", "evidence_ref": "SYNTHETIC inception"}
        }
    )
    _, result, calls = collected(p)
    assert len(calls) == 3 and not result.series[0].chunks
    assert result.series[0].unavailable_before_inception == (p.start, p.end)


@pytest.mark.parametrize(
    "status,body,code",
    [
        (429, b"", "RATE_LIMITED"),
        (401, b"", "AUTH_INVALID_OR_EXPIRED"),
        (503, b"", "PROVIDER_SERVICE_ERROR"),
        (403, b'{"errorCode":"806"}', "DATA_ENTITLEMENT_REQUIRED"),
        (200, b"{}", "UNEXPECTED_RESPONSE"),
    ],
)
def test_provider_failure_stops_without_partial_import_candidates(status, body, code):
    p = plan()

    def handler(r, n):
        return httpx.Response(
            status if n == 2 else 200,
            content=body if n == 2 else body_for(r, p.calendar),
            headers={"Content-Type": "application/json"},
        )

    provider, calls = provider_for(p, handler=handler)
    result = collect_history(provider, p, request_approved=True, pause=lambda _: None)
    assert len(calls) == result.attempted_requests == 2 and result.failure_code == code
    assert not result.series and result.unattempted_symbols == ("GOLDBEES", "SILVERBEES")


@pytest.mark.parametrize(
    "field,value", [("volume", 1.5), ("timestamp", 0), ("high", 1), ("close", "secret")]
)
def test_bad_provider_ohlcv_stops_batch(field, value):
    p = plan()

    def change(data):
        data[field][0] = value

    provider, calls = provider_for(p, change=change)
    result = collect_history(provider, p, request_approved=True)
    assert len(calls) == 1 and not result.series and result.failure_code == "INVALID_DATA"


def test_network_timeout_stops_once():
    p = plan()

    def handler(r, n):
        raise httpx.ReadTimeout(TOKEN)

    provider, calls = provider_for(p, handler=handler)
    result = collect_history(provider, p, request_approved=True)
    assert len(calls) == 1 and result.failure_code == "NETWORK_TIMEOUT"
    assert TOKEN not in json.dumps(result.safe_summary())


def test_inter_request_control_failure_never_makes_next_call():
    p = plan()
    provider, calls = provider_for(p)

    def broken(_):
        raise RuntimeError(TOKEN)

    result = collect_history(provider, p, request_approved=True, pause=broken)
    assert (
        len(calls) == 1
        and result.attempted_requests == 1
        and result.failure_code == "PROVIDER_OR_CONTROL_ERROR"
    )


def test_preflight_command_no_network_or_database(tmp_path, capsys):
    p = plan()
    provider, calls = provider_for(p)
    path = tmp_path / "plan.json"
    path.write_text(p.model_dump_json())
    code = main(
        ["--plan", str(path), "--env-file", str(tmp_path / "missing.env")],
        provider_factory=lambda _: provider,
        session_factory=lambda: pytest.fail("database constructed"),
    )
    assert code == 0 and not calls
    report = json.loads(capsys.readouterr().out)
    assert report["expected_requests"] == 4


def test_mismatched_review_fingerprint_blocks_execution(tmp_path, capsys):
    p = plan()
    provider, calls = provider_for(p)
    path = tmp_path / "plan.json"
    path.write_text(p.model_dump_json())
    assert (
        main(
            [
                "--plan",
                str(path),
                "--env-file",
                str(tmp_path / "none"),
                "--execute-approved-plan",
                "wrong",
            ],
            provider_factory=lambda _: provider,
        )
        == 2
    )
    assert not calls and json.loads(capsys.readouterr().out)["code"] == "REVIEWED_PLAN_MISMATCH"


def test_approved_transient_execution_never_constructs_database(tmp_path, capsys):
    p = plan()
    provider, calls = provider_for(p)
    path = tmp_path / "plan.json"
    path.write_text(p.model_dump_json())
    fingerprint = preflight(provider, p)["plan_fingerprint"]
    assert (
        main(
            [
                "--plan",
                str(path),
                "--env-file",
                str(tmp_path / "none"),
                "--execute-approved-plan",
                fingerprint,
            ],
            provider_factory=lambda _: provider,
            session_factory=lambda: pytest.fail("database"),
            pause=lambda _: None,
        )
        == 0
    )
    output = capsys.readouterr().out
    assert len(calls) == 4 and TOKEN not in output and '"close"' not in output
    assert json.loads(output)["persistence"] == "NOT_REQUESTED_NO_DATABASE"
