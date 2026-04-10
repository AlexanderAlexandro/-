from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.common import main_menu_keyboard
from services.static_service import get_main_menu_text, get_unknown_message_text
from utils.messages import safe_edit_text


router = Router()


@router.callback_query(F.data == "menu:main")
async def open_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit_text(
        callback,
        get_main_menu_text(),
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.chat.type == ChatType.PRIVATE)
async def fallback_message(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        f"{get_unknown_message_text()}\n\n{get_main_menu_text()}",
        reply_markup=main_menu_keyboard(),
    )
