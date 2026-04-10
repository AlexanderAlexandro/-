from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.static_service import list_useful_blocks


def useful_blocks_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=block.title, callback_data=f"useful:{block.id}")]
        for block in list_useful_blocks()
    ]
    rows.append(
        [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def useful_block_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="menu:useful"),
                InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
            ]
        ]
    )
