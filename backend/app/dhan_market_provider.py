"""Bounded read-only quote/intraday adapter. Uses the existing verified catalog.

No SDK, account endpoints, token exchange, raw-response persistence or retries.
"""

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import time
import httpx
from .daily_values import price
from .dhan_provider import DhanDailyProvider, _listing
from .dhan_http import configuration_problem, live_transport, quiet_request_logs, ERROR_CODES
from .dhan_history_contract import _object, MIN_CANDIDATE_SECONDS, MAX_CANDIDATE_SECONDS
from .market_data import ProviderFailure
from .market_session import (
    IST,
    INTERVALS,
    MarketQuote,
    IntradayCandle,
    SessionResult,
    regular_bounds,
)

API = "https://api.dhan.co/v2"


def financial(value, *, optional=False):
    if optional and (value is None or type(value) in (int, Decimal) and value == 0):
        return None
    if type(value) not in (int, Decimal):
        raise ValueError("INVALID_PRICE")
    return price(str(value) if type(value) is int else format(value, "f"))


def integral(value):
    if type(value) not in (int, Decimal) or not 0 <= value <= 2**63 - 1:
        raise ValueError("INVALID_INTEGER")
    if isinstance(value, Decimal) and (not value.is_finite() or value != value.to_integral_value()):
        raise ValueError("INVALID_INTEGER")
    return int(value)


def epoch_seconds(value):
    stamp = integral(value)
    if not MIN_CANDIDATE_SECONDS <= stamp <= MAX_CANDIDATE_SECONDS:
        raise ValueError("INVALID_EPOCH_SECONDS")
    return datetime.fromtimestamp(stamp, IST)


def quote_time(value, retrieved):
    if not isinstance(value, str) or len(value) > 40:
        return None
    # Explicit observed policy, not format/unit inference from numeric magnitude.
    try:
        parsed = datetime.strptime(value, "%d/%m/%Y %H:%M:%S").replace(tzinfo=IST)
        if not date(2000, 1, 1) <= parsed.date() < date(
            2100, 1, 1
        ) or parsed > retrieved + timedelta(seconds=5):
            return None
        return parsed
    except ValueError:
        return None


class DhanMarketProvider(DhanDailyProvider):
    timestamp_policy = "EXPLICIT_UNIX_SECONDS_AND_DDMMYYYY_IST_CORROBORATED_NOT_UNIVERSAL_CONTRACT"

    def __init__(self, *args, clock=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _request(self, path, body, *, client_id=False):
        problem = configuration_problem(self._config)
        if problem:
            return None, SessionResult(failure=ProviderFailure(problem)), None
        creds = self._config.credentials
        if client_id and (creds.client_id is None or not creds.client_id.get_secret_value()):
            return None, SessionResult(failure=ProviderFailure("MISSING_CLIENT_ID")), None
        headers = {
            "access-token": creds.access_token.get_secret_value(),
            "Content-Type": "application/json",
        }
        if client_id:
            headers["client-id"] = creds.client_id.get_secret_value()
        status, attempts = None, 0
        try:
            with (
                quiet_request_logs(),
                httpx.Client(
                    transport=(self._transport_factory or live_transport)(),
                    timeout=self._timeout,
                    trust_env=False,
                    follow_redirects=False,
                    headers={"Accept": "application/json", "Accept-Encoding": "identity"},
                ) as client,
            ):
                attempts = 1
                with client.stream("POST", API + path, json=body, headers=headers) as response:
                    status = response.status_code
                    if status == 429 or status >= 500 or 300 <= status < 400:
                        code = (
                            "RATE_LIMITED"
                            if status == 429
                            else "PROVIDER_SERVICE_ERROR"
                            if status >= 500
                            else "REDIRECT_REFUSED"
                        )
                        return (
                            None,
                            SessionResult(attempts, status, failure=ProviderFailure(code, status)),
                            None,
                        )
                    if response.headers.get("Content-Encoding", "identity") != "identity":
                        raise ValueError()
                    data, began = bytearray(), time.monotonic()
                    for chunk in response.iter_bytes():
                        if (
                            len(data) + len(chunk) > 4 * 1024 * 1024
                            or time.monotonic() - began > 20
                        ):
                            raise ValueError()
                        data.extend(chunk)
                    obj = _object(bytes(data))
                    retrieved = self.clock()
                    if (
                        obj is None
                        or response.headers.get("Content-Type", "").split(";")[0]
                        != "application/json"
                    ):
                        raise ValueError()
                    if status in (401, 403) or any(
                        k in obj for k in ("errorCode", "errorType", "errorMessage")
                    ):
                        code = ERROR_CODES.get(
                            str(obj.get("errorCode")),
                            "AUTH_INVALID_OR_EXPIRED"
                            if status == 401
                            else "ACCESS_DENIED"
                            if status == 403
                            else "PROVIDER_REQUEST_REJECTED",
                        )
                        return (
                            None,
                            SessionResult(attempts, status, failure=ProviderFailure(code, status)),
                            retrieved,
                        )
                    if status != 200:
                        return (
                            None,
                            SessionResult(
                                attempts,
                                status,
                                failure=ProviderFailure("PROVIDER_REQUEST_REJECTED", status),
                            ),
                            retrieved,
                        )
                    return obj, SessionResult(attempts, status), retrieved
        except httpx.TimeoutException:
            code = "NETWORK_TIMEOUT"
        except (httpx.RequestError, OSError):
            code = "NETWORK_ERROR"
        except Exception:
            code = "UNEXPECTED_RESPONSE"
        return None, SessionResult(attempts, status, failure=ProviderFailure(code, status)), None

    def retrieve_quotes(self):
        obj, result, retrieved = self._request(
            "/marketfeed/quote",
            {"NSE_EQ": [int(x.security_id) for x in self._instruments]},
            client_id=True,
        )
        if result.failure:
            return result
        try:
            group = obj["data"]["NSE_EQ"]
            if not isinstance(group, dict) or obj.get("status") != "success":
                raise ValueError()
            quotes, issues = [], []
            for item in self._instruments:
                q = group.get(item.security_id)
                if not isinstance(q, dict):
                    issues.append(item.symbol + ":QUOTE_MISSING")
                    continue
                try:
                    o = q["ohlc"]
                    ltp = financial(q["last_price"])
                    opening, high, low = (
                        financial(o.get(k), optional=True) for k in ["open", "high", "low"]
                    )
                    closing = financial(o.get("close"), optional=True)
                    if (
                        high is not None
                        and low is not None
                        and (high < low or opening is not None and not low <= opening <= high)
                    ):
                        raise ValueError()
                    previous, basis = None, "UNAVAILABLE"
                    change = q.get("net_change")
                    if (
                        type(change) in (int, Decimal)
                        and Decimal(change).is_finite()
                        and abs(change) < Decimal("1e14")
                    ):
                        previous = financial(ltp - change)
                        basis = "DERIVED_FROM_DOCUMENTED_NET_CHANGE"
                        if closing is not None and closing == previous:
                            basis = "NET_CHANGE_CORROBORATED_BY_PROVIDER_CLOSE"
                    warnings = []
                    if previous is not None and closing is not None and previous != closing:
                        warnings.append(
                            "PROVIDER_CLOSE_DIFFERS_PREVIOUS_CLOSE_DERIVED_FROM_NET_CHANGE"
                        )
                    if previous is None:
                        warnings.append("PREVIOUS_CLOSE_UNVERIFIED_CHANGE_UNAVAILABLE")
                    stamp = quote_time(q.get("last_trade_time"), retrieved)
                    if stamp is None:
                        warnings.append("LAST_TRADE_TIME_UNAVAILABLE_OR_INVALID")
                    quote = MarketQuote(
                        _listing(item),
                        ltp,
                        opening,
                        high,
                        low,
                        previous,
                        closing,
                        integral(q["volume"]) if q.get("volume") is not None else None,
                        stamp,
                        retrieved,
                        basis,
                    )
                    quotes.append(replace(quote, warnings=quote.warnings + tuple(warnings)))
                except (ValueError, ArithmeticError, KeyError, TypeError, AttributeError):
                    issues.append(item.symbol + ":QUOTE_REJECTED")
            return replace(result, quotes=tuple(quotes), issues=tuple(issues))
        except (KeyError, TypeError, ValueError):
            return replace(
                result, failure=ProviderFailure("UNEXPECTED_RESPONSE", result.http_status)
            )

    def retrieve_intraday(self, listing, interval, start, end):
        item = next((x for x in self._instruments if _listing(x) == listing), None)
        if (
            item is None
            or type(interval) is not int
            or interval not in INTERVALS
            or type(start) is not date
            or type(end) is not date
            or not date(2000, 1, 1) <= start <= end < date(2100, 1, 1)
            or (end - start).days >= 90
        ):
            return SessionResult(failure=ProviderFailure("INVALID_INTRADAY_REQUEST"))
        # Midnight bounds include the opening bar despite observed strict fromDate filtering.
        body = {
            "securityId": item.security_id,
            "exchangeSegment": "NSE_EQ",
            "instrument": "EQUITY",
            "interval": str(interval),
            "oi": False,
            "fromDate": start.isoformat() + " 00:00:00",
            "toDate": (end + timedelta(days=1)).isoformat() + " 00:00:00",
        }
        obj, result, retrieved = self._request("/charts/intraday", body)
        if result.failure:
            return result
        try:
            fields = ("open", "high", "low", "close", "volume", "timestamp")
            if not all(isinstance(obj.get(k), list) for k in fields):
                raise ValueError()
            n = len(obj["timestamp"])
            if n > 40000 or any(len(obj[k]) != n for k in fields):
                raise ValueError()
            rows, seen = [], set()
            for i in range(n):
                at = epoch_seconds(obj["timestamp"][i])
                opening, high, low, closing = (financial(obj[k][i]) for k in fields[:4])
                volume = integral(obj["volume"][i])
                session_open, session_close = regular_bounds(at.date())
                if (
                    at in seen
                    or not start <= at.date() <= end
                    or at > retrieved + timedelta(seconds=5)
                    or not session_open <= at < session_close
                    or int((at - session_open).total_seconds()) % (interval * 60)
                    or not low <= opening <= high
                    or not low <= closing <= high
                ):
                    raise ValueError()
                seen.add(at)
                boundary = min(at + timedelta(minutes=interval), session_close)
                classification = (
                    "INTRADAY_COMPLETED"
                    if boundary <= retrieved - timedelta(seconds=60)
                    else "INTRADAY_PROVISIONAL"
                )
                rows.append(
                    IntradayCandle(
                        listing,
                        at,
                        boundary,
                        interval,
                        opening,
                        high,
                        low,
                        closing,
                        volume,
                        retrieved,
                        str(obj["timestamp"][i]),
                        i + 1,
                        classification=classification,
                        requested_start=start,
                        requested_end=end,
                        volume_semantics="PER_CANDLE_VOLUME",
                    )
                )
            return replace(result, candles=tuple(sorted(rows, key=lambda r: r.start)))
        except (ValueError, ArithmeticError, KeyError, TypeError, OverflowError):
            return replace(
                result, failure=ProviderFailure("INVALID_INTRADAY_DATA", result.http_status)
            )
