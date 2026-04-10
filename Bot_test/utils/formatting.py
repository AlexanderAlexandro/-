from __future__ import annotations

from collections.abc import Iterable

from utils.text import escape_html


def render_screen(
    title: str,
    sections: Iterable[str] | None = None,
    *,
    emoji: str | None = None,
) -> str:
    decorated_title = f"{emoji} {title}" if emoji else title
    parts = [f"<b>{escape_html(decorated_title)}</b>"]

    if sections:
        parts.extend(section for section in sections if section)

    return "\n\n".join(parts)


def render_label_block(label: str, value: str) -> str:
    return f"<b>{escape_html(label)}</b>\n{escape_html(value)}"


def render_copy_block(label: str, value: str) -> str:
    return f"<b>{escape_html(label)}</b>\n<pre>{escape_html(value)}</pre>"


def render_hint(text: str) -> str:
    return f"<i>{escape_html(text)}</i>"


def render_bullets(items: Iterable[str]) -> str:
    return "\n".join(f"• {escape_html(item)}" for item in items if item)

