from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _chunk_buttons(
    choice_buttons: list[tuple[str, str]],
    *,
    chunk_size: int = 2,
) -> list[list[InlineKeyboardButton]]:
    rows: list[list[InlineKeyboardButton]] = []
    for index in range(0, len(choice_buttons), chunk_size):
        rows.append(
            [
                InlineKeyboardButton(text=label, callback_data=f"flowans:{value}")
                for value, label in choice_buttons[index : index + chunk_size]
            ]
        )
    return rows


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Шаблоны", callback_data="menu:templates"),
                InlineKeyboardButton(text="Калькуляторы", callback_data="menu:calculators"),
            ],
            [
                InlineKeyboardButton(text="Лендинги и стартап", callback_data="menu:kit"),
            ],
            [
                InlineKeyboardButton(text="Полезное", callback_data="menu:useful"),
                InlineKeyboardButton(text="О боте", callback_data="menu:about"),
            ],
        ]
    )


def menu_only_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")],
        ]
    )


def section_keyboard(back_callback: str, back_label: str = "Назад") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=back_label, callback_data=back_callback),
                InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
            ]
        ]
    )


def flow_keyboard(
    section_callback: str,
    section_label: str,
    show_back: bool = True,
    choice_buttons: list[tuple[str, str]] | None = None,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    if choice_buttons:
        rows.extend(_chunk_buttons(choice_buttons))

    navigation_row: list[InlineKeyboardButton] = []
    if show_back:
        navigation_row.append(
            InlineKeyboardButton(text="Назад", callback_data="flow:back")
        )
    navigation_row.append(
        InlineKeyboardButton(text=section_label, callback_data=section_callback)
    )
    rows.append(navigation_row)
    rows.append(
        [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def result_keyboard(
    retry_callback: str,
    section_callback: str,
    section_label: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Собрать заново", callback_data=retry_callback)],
            [
                InlineKeyboardButton(text=section_label, callback_data=section_callback),
                InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
            ],
        ]
    )
