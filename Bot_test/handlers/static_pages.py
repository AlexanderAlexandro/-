from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.common import menu_only_keyboard
from keyboards.static_pages import useful_block_keyboard, useful_blocks_keyboard
from services.static_service import (
    get_about_text,
    get_useful_section_text,
    render_useful_block,
)
from utils.messages import safe_edit_text


router = Router()


@router.callback_query(F.data == "menu:useful")
async def open_useful(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit_text(
        callback,
        get_useful_section_text(),
        reply_markup=useful_blocks_keyboard(),
    )


@router.callback_query(F.data.startswith("useful:"))
async def open_useful_block(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    block_id = callback.data.split(":", maxsplit=1)[1]
    await safe_edit_text(
        callback,
        render_useful_block(block_id),
        reply_markup=useful_block_keyboard(),
    )


@router.callback_query(F.data == "menu:about")
async def open_about(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit_text(
        callback,
        get_about_text(),
        reply_markup=menu_only_keyboard(),
    )
