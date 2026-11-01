import base64
import hashlib
import hmac
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID
from .errors import APIError


def plain(value):
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if hasattr(value, "__table__"):
        return {c.name: plain(getattr(value, c.name)) for c in value.__table__.columns}
    return value


def canonical(value) -> str:
    return json.dumps(plain(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def encode_cursor(value, token: str) -> str:
    raw = canonical(value).encode()
    signature = hmac.new(token.encode(), raw, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature + raw).decode().rstrip("=")


def decode_cursor(value: str, token: str, scope: str):
    try:
        if len(value) > 4096:
            raise ValueError()
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        sig, body = raw[:32], raw[32:]
        if not hmac.compare_digest(sig, hmac.new(token.encode(), body, hashlib.sha256).digest()):
            raise ValueError()
        data = json.loads(body)
        if data["scope"] != scope:
            raise APIError(
                409, "SNAPSHOT_CHANGED", "The query or dataset changed. Reload from the first page."
            )
        return data["last"]
    except APIError:
        raise
    except (ValueError, KeyError, TypeError):
        raise APIError(422, "INVALID_CURSOR", "Invalid pagination cursor.") from None
