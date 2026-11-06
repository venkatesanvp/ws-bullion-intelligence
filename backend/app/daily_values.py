"""Shared exact canonical price validation (DC-02/04); no I/O."""

import re
from decimal import Decimal, InvalidOperation


def price(value: str) -> Decimal:
    if not re.fullmatch(r"[+]?(?:\d+(?:\.\d*)?|\.\d+)", value):
        raise ValueError()
    try:
        d = Decimal(value)
        if not d.is_finite() or d <= 0 or d >= Decimal("100000000000000"):
            raise ValueError()
        if d.as_tuple().exponent < -10:
            raise ValueError()
        return d
    except InvalidOperation:
        raise ValueError() from None
