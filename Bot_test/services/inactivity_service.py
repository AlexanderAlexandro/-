from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from aiogram import Bot

from config import get_settings
from services.chat_log_service import get_inactive_chats, mark_inactivity_reminder_sent


logger = logging.getLogger(__name__)
CHECK_INTERVAL_SECONDS = 60 * 60


async def send_inactivity_reminders(bot: Bot) -> None:
    settings = get_settings()
    for chat in get_inactive_chats(inactivity_days=settings.inactivity_reminder_days):
        try:
            await bot.send_message(chat.chat_id, settings.inactivity_reminder_text)
            mark_inactivity_reminder_sent(chat.chat_id)
        except Exception:
            logger.exception(
                "Не удалось отправить напоминание о тишине в чат %s",
                chat.chat_id,
            )


async def inactivity_monitor(bot: Bot) -> None:
    try:
        while True:
            await send_inactivity_reminders(bot)
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        raise


async def shutdown_task(task: asyncio.Task[None]) -> None:
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
