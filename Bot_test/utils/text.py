from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from html import escape, unescape


HTML_TAG_RE = re.compile(r"<[^>]+>")


def escape_html(value: str) -> str:
    return escape(value, quote=False)


def format_number(value: Decimal, precision: int = 2) -> str:
    quant = Decimal("1") if precision == 0 else Decimal("1." + ("0" * precision))
    rounded = value.quantize(quant, rounding=ROUND_HALF_UP)
    rendered = f"{rounded:,.{precision}f}" if precision > 0 else f"{rounded:,.0f}"

    if precision > 0:
        rendered = rendered.rstrip("0").rstrip(".")

    return rendered.replace(",", " ").replace(".", ",")


def strip_html(value: str) -> str:
    plain_text = HTML_TAG_RE.sub("", value)
    return unescape(plain_text).replace("\xa0", " ").strip()


def truncate_text(value: str, max_length: int = 3000) -> str:
    normalized = value.strip()
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 1].rstrip() + "…"

