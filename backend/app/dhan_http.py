"""Shared backend-only Dhan HTTP policy; construction makes no request."""

from contextlib import contextmanager
import logging
import threading
import httpx
from .dhan_config import DhanConfiguration

TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)

# Provider strings/messages are never returned; only these documented codes.
ERROR_CODES = {
    "807": "TOKEN_EXPIRED",
    "808": "INVALID_CREDENTIALS",
    "809": "INVALID_CREDENTIALS",
    "810": "INVALID_CREDENTIALS",
    "806": "DATA_ENTITLEMENT_REQUIRED",
    "805": "RATE_LIMITED",
    "800": "PROVIDER_SERVICE_ERROR",
    "804": "PROVIDER_REQUEST_REJECTED",
    "811": "PROVIDER_REQUEST_REJECTED",
    "812": "PROVIDER_REQUEST_REJECTED",
    "813": "PROVIDER_REQUEST_REJECTED",
    "814": "PROVIDER_REQUEST_REJECTED",
    "DH-901": "AUTH_INVALID_OR_EXPIRED",
    "DH-902": "ACCESS_OR_ENTITLEMENT_REQUIRED",
    "DH-903": "ACCOUNT_ACCESS_RESTRICTED",
    "DH-904": "RATE_LIMITED",
    "DH-905": "PROVIDER_REQUEST_REJECTED",
    "DH-907": "PROVIDER_REQUEST_REJECTED",
    "DH-908": "PROVIDER_SERVICE_ERROR",
    "DH-909": "NETWORK_ERROR",
    "DH-910": "PROVIDER_ERROR",
}


def configuration_problem(config: DhanConfiguration) -> str | None:
    if not config.values_valid:
        return "INVALID_CONFIGURATION"
    if not config.enabled:
        return "INTEGRATION_DISABLED"
    if not config.runtime_configuration_complete or config.credentials is None:
        return "MISSING_ACCESS_TOKEN"
    return None


@contextmanager
def _quiet_transport_logs():
    # This standalone CLI must not emit library wire/debug messages. No web-app hook.
    previous = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        yield
    finally:
        logging.disable(previous)


def live_transport() -> httpx.HTTPTransport:
    return httpx.HTTPTransport(
        verify=True,
        trust_env=False,
        retries=0,
        limits=httpx.Limits(max_connections=1, max_keepalive_connections=0),
    )


@contextmanager
def quiet_request_logs():
    """Suppress only this request thread on existing configured handlers.

    The adapter has no logging calls and HTTPX/httpcore configure no handlers.
    Unlike the historical standalone CLI guard, other application threads keep
    their logging. Configure handlers before running acquisition operations.
    """
    owner = threading.get_ident()

    class RequestFilter(logging.Filter):
        def filter(self, record):
            return record.thread != owner

    handlers = set(logging.getLogger().handlers)
    for logger in tuple(logging.root.manager.loggerDict.values()):
        if isinstance(logger, logging.Logger):
            handlers.update(logger.handlers)
    if logging.lastResort is not None:
        handlers.add(logging.lastResort)
    guard = RequestFilter()
    for handler in handlers:
        handler.addFilter(guard)
    try:
        yield
    finally:
        for handler in handlers:
            handler.removeFilter(guard)
