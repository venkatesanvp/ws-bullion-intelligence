"""One backend-wide provider request slot/rate/circuit budget. No retries."""

from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
from threading import Lock
import time
import json
import logging
from .errors import APIError


class ProviderBudget:
    def __init__(self, limit=10000, *, clock=None, monotonic=time.monotonic, pause=time.sleep):
        self.lock = Lock()
        self.limit = limit
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.monotonic, self.pause = monotonic, pause
        self.last = 0.0
        self.day = None
        self.attempts = 0
        self.blocked_until = None

    def invoke(self, action, *, operation="UNSPECIFIED"):
        if operation not in {"UNSPECIFIED", "DAILY_HISTORY", "QUOTE", "INTRADAY"}:
            raise ValueError("Unknown provider operation")
        if not self.lock.acquire(timeout=30):
            raise APIError(
                503, "PROVIDER_BUSY", "Market-data provider is busy; cached data remains available."
            )
        try:
            now = self.clock()
            if self.blocked_until and now < self.blocked_until:
                raise APIError(
                    429,
                    "PROVIDER_BACKOFF",
                    "Market-data requests are paused after a provider failure.",
                )
            if self.day != now.date():
                self.day, self.attempts = now.date(), 0
            if self.attempts >= self.limit:
                raise APIError(429, "LOCAL_DAILY_BUDGET", "Local provider daily budget reached.")
            remaining = 1 - (self.monotonic() - self.last)
            if remaining > 0:
                self.pause(remaining)
            before = self.attempts
            try:
                result = action()
            except Exception:
                logging.getLogger("bullion").warning(json.dumps({
                    "event": "PROVIDER_OPERATION_ABORTED", "operation": operation,
                    "counter_before": before, "counter_after": self.attempts,
                }))
                raise
            self.attempts += result.request_attempts
            logging.getLogger("bullion").info(json.dumps({
                "event": "PROVIDER_OPERATION_COMPLETED", "operation": operation,
                "request_attempts": result.request_attempts,
                "counter_before": before, "counter_after": self.attempts,
                "failed": result.failure is not None,
            }))
            self.last = self.monotonic()
            if result.failure and result.failure.code in {
                "TOKEN_EXPIRED",
                "INVALID_CREDENTIALS",
                "AUTH_INVALID_OR_EXPIRED",
                "ACCESS_DENIED",
                "DATA_ENTITLEMENT_REQUIRED",
                "RATE_LIMITED",
                "PROVIDER_SERVICE_ERROR",
                "NETWORK_TIMEOUT",
                "NETWORK_ERROR",
            }:
                self.blocked_until = now + timedelta(minutes=5)
            return result
        finally:
            self.lock.release()


@contextmanager
def operation_slot(lock, cancel=None):
    started = time.monotonic()
    while not lock.acquire(timeout=0.1):
        if cancel is not None and cancel.is_set():
            raise APIError(499, "CANCELLED", "Market-data operation cancelled while waiting.")
        if time.monotonic() - started > 120:
            raise APIError(503, "PROVIDER_BUSY", "Market-data operation queue is busy.")
    try:
        yield
    finally:
        lock.release()
