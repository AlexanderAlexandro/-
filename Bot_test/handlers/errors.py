from __future__ import annotations

import logging
from contextlib import suppress

from aiogram import Router
from aiogram.types import ErrorEvent


router = Router()
logger = logging.getLogger(__name__)


@router.error()
async def global_error_handler(event: ErrorEvent) -> bool:
    logger.exception("Unhandled error while processing update", exc_info=event.exception)

    if event.update.message:
        with suppress(Exception):
            await event.update.message.answer(
                "Произошла ошибка. Попробуйте еще раз или начните заново через /start."
            )

    if event.update.callback_query:
        with suppress(Exception):
            await event.update.callback_query.answer(
                "Произошла ошибка. Попробуйте еще раз.",
                show_alert=True,
            )

    return True

