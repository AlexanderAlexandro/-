from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.chat_kit import chat_kit_keyboard
from services.static_service import get_kit_text
from utils.messages import safe_edit_text


router = Router()


@router.message(Command("kit"), StateFilter("*"))
async def open_kit_from_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(get_kit_text(), reply_markup=chat_kit_keyboard())


@router.callback_query(F.data == "menu:kit")
async def open_kit_from_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit_text(
        callback,
        get_kit_text(),
        reply_markup=chat_kit_keyboard(),
    )
