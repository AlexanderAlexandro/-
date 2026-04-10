from __future__ import annotations

import logging
from datetime import datetime

from aiogram import Bot
from aiogram.types import User

from config import get_settings
from utils.formatting import render_screen
from utils.text import escape_html, strip_html, truncate_text


logger = logging.getLogger(__name__)


def _format_user_name(user: User) -> str:
    full_name = " ".join(
        part for part in [user.first_name, user.last_name] if part
    ).strip()
    if user.username:
        return f"{full_name} (@{user.username})" if full_name else f"@{user.username}"
    return full_name or str(user.id)


def build_owner_report_text(
    *,
    section_title: str,
    scenario_title: str,
    result_text: str,
    user: User,
) -> str:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    result_preview = truncate_text(strip_html(result_text), max_length=2600)

    return render_screen(
        "Отчет владельцу",
        [
            f"<b>Раздел</b>\n{escape_html(section_title)}",
            f"<b>Сценарий</b>\n{escape_html(scenario_title)}",
            f"<b>Пользователь</b>\n{escape_html(_format_user_name(user))}",
            f"<b>User ID</b>\n{user.id}",
            f"<b>Время</b>\n{escape_html(timestamp)}",
            f"<b>Результат</b>\n<pre>{escape_html(result_preview)}</pre>",
        ],
        emoji="📬",
    )


async def send_owner_report(
    *,
    bot: Bot,
    section_title: str,
    scenario_title: str,
    result_text: str,
    user: User | None,
) -> None:
    if user is None:
        return

    settings = get_settings()
    if settings.owner_telegram_id is None:
        return

    report_text = build_owner_report_text(
        section_title=section_title,
        scenario_title=scenario_title,
        result_text=result_text,
        user=user,
    )

    try:
        await bot.send_message(settings.owner_telegram_id, report_text)
    except Exception:
        logger.exception("Не удалось отправить отчет владельцу.")
