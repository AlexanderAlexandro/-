from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from config import get_settings
from handlers.admin import router as admin_router
from handlers.calculators import router as calculators_router
from handlers.chat_kit import router as chat_kit_router
from handlers.errors import router as errors_router
from handlers.navigation import router as navigation_router
from handlers.start import router as start_router
from handlers.static_pages import router as static_pages_router
from handlers.templates import router as templates_router
from services.inactivity_service import inactivity_monitor, shutdown_task
from services.runtime_control import clear_stop_callback, register_stop_callback
from utils.chat_logging import ChatLoggingMiddleware


async def set_bot_commands(bot: Bot) -> None:
    public_commands = [
        BotCommand(command="start", description="Открыть главное меню"),
        BotCommand(command="kit", description="Быстрый набор для чата"),
        BotCommand(command="help", description="Как пользоваться ботом"),
        BotCommand(command="stop", description="Остановить текущий сценарий"),
    ]
    await bot.set_my_commands(
        public_commands,
        scope=BotCommandScopeDefault(),
    )

    settings = get_settings()
    if settings.owner_telegram_id is not None:
        await bot.set_my_commands(
            [
                *public_commands,
                BotCommand(command="admin", description="Панель владельца"),
                BotCommand(command="shutdown", description="Остановить процесс бота"),
            ],
            scope=BotCommandScopeChat(chat_id=settings.owner_telegram_id),
        )


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings = get_settings()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Храним состояние только в памяти процесса, без базы данных и без постоянного сохранения.
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.outer_middleware(ChatLoggingMiddleware())

    dp.include_router(start_router)
    dp.include_router(chat_kit_router)
    dp.include_router(admin_router)
    dp.include_router(templates_router)
    dp.include_router(calculators_router)
    dp.include_router(static_pages_router)
    dp.include_router(navigation_router)
    dp.include_router(errors_router)

    await set_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    register_stop_callback(dp.stop_polling)
    reminder_task = asyncio.create_task(inactivity_monitor(bot))
    try:
        await dp.start_polling(bot)
    finally:
        clear_stop_callback()
        await shutdown_task(reminder_task)


if __name__ == "__main__":
    asyncio.run(main())
