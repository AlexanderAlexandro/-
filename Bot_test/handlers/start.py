from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.common import main_menu_keyboard
from services.static_service import (
    get_help_text,
    get_main_menu_text,
    get_stop_flow_text,
    get_welcome_text,
)


router = Router()


@router.message(CommandStart(), StateFilter("*"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(get_welcome_text(), reply_markup=main_menu_keyboard())


@router.message(Command("menu"), StateFilter("*"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(get_main_menu_text(), reply_markup=main_menu_keyboard())


@router.message(Command("help"), StateFilter("*"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(get_help_text(), reply_markup=main_menu_keyboard())


@router.message(Command("stop"), StateFilter("*"))
async def cmd_stop(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(get_stop_flow_text(), reply_markup=main_menu_keyboard())
