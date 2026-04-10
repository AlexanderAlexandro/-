from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.calculator_service import list_calculators


def calculators_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=calculator.title, callback_data=f"calc:{calculator.id}")]
        for calculator in list_calculators()
    ]
    rows.append(
        [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def calculator_card_keyboard(calculator_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Начать расчет",
                    callback_data=f"calcstart:{calculator_id}",
                )
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="menu:calculators"),
                InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
            ],
        ]
    )
