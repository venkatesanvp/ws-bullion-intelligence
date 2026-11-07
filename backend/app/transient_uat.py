"""Explicit, authenticated, once-per-process four-request transient UAT loader."""

import os
from fastapi import Request
from pydantic import Field
from .acquisition import HistoryPlan, collect_history, preflight
from .dhan_config import load_dhan_configuration
from .dhan_provider import DhanDailyProvider
from .errors import APIError
from .schemas import Strict

APPROVED_FINGERPRINT = "a051f5383ab4f6bb8959ffb845962a58597cf58c7483dfeebe1efb632aa9dbe9"
NAMES = {
    "TATAGOLD": "Tata Gold ETF",
    "TATSILV": "Tata Silver ETF",
    "GOLDBEES": "Nippon India Gold BeES",
    "SILVERBEES": "Nippon India Silver BeES",
}


class TransientLoad(Strict):
    plan: HistoryPlan
    plan_fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    live_approved: bool = False


def register_transient_uat(router, respond):
    @router.get("/transient-session")
    def status(request: Request):
        report = request.app.state.transient_research.report()
        if request.app.state.settings.market_data_enabled:
            report["live_requests"] = request.app.state.market_data.attempted_requests
        return respond(request, report)

    @router.post("/transient-session/dhan-history")
    def load(body: TransientLoad, request: Request):
        if request.app.state.settings.market_data_enabled:
            raise APIError(
                409,
                "USE_MARKET_DATA_SERVICE",
                "Standing retrieval is active. Use Apply range; the legacy diagnostic loader is disabled.",
            )
        if body.live_approved is not True:
            raise APIError(
                403, "LIVE_APPROVAL_REQUIRED", "Explicit live authorization is required."
            )
        # Enablement exists only in this call's configuration; os.environ/.env stay unchanged.
        config = load_dhan_configuration(environ={**os.environ, "DHAN_DATA_API_ENABLED": "true"})
        factory = request.app.state.transient_provider_factory or DhanDailyProvider
        provider = factory(config)
        report = preflight(provider, body.plan)
        if (
            body.plan_fingerprint != APPROVED_FINGERPRINT
            or report["plan_fingerprint"] != APPROVED_FINGERPRINT
            or report["expected_requests"] != 4
        ):
            raise APIError(
                409, "REVIEWED_PLAN_MISMATCH", "Use the owner-approved four-ETF one-year plan."
            )
        store = request.app.state.transient_research
        store.claim()  # Set before transport: concurrent/duplicate commands cannot make another batch.
        result = collect_history(provider, body.plan, request_approved=True)
        if result.status != "COLLECTED_UNQUALIFIED":
            summary = result.safe_summary()
            store.record_failure(summary)
            return respond(request, summary, status=502)
        try:
            summary = store.install(
                result,
                body.plan,
                names=NAMES,
                data_class="SYNTHETIC_TEST"
                if request.app.state.transient_provider_factory
                else "REAL_MARKET",
            )
        except APIError:
            store.record_failure(
                {
                    "status": "CANONICAL_VALIDATION_FAILED",
                    "acquisition": result.safe_summary(),
                    "live_requests": result.attempted_requests,
                }
            )
            raise
        return respond(request, summary, status=201)
