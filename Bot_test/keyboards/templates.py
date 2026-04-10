from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.template_service import list_categories, list_templates_by_category


def template_categories_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=category.title, callback_data=f"tmplcat:{category.id}")]
        for category in list_categories()
    ]
    rows.append(
        [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def template_list_keyboard(category_id: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=template.title, callback_data=f"tmpl:{template.id}")]
        for template in list_templates_by_category(category_id)
    ]
    rows.append(
        [
            InlineKeyboardButton(text="Назад", callback_data="menu:templates"),
            InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def template_actions_keyboard(template_id: str, category_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Показать шаблон",
                    callback_data=f"taction:{template_id}:show",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Собрать по шагам",
                    callback_data=f"taction:{template_id}:build",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=f"tmplcat:{category_id}",
                ),
                InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
            ],
        ]
    )


def template_build_intro_keyboard(template_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Начать сборку",
                    callback_data=f"taction:{template_id}:start",
                )
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=f"tmpl:{template_id}"),
                InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
            ],
        ]
    )


def template_preview_keyboard(template_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Собрать по шагам",
                    callback_data=f"taction:{template_id}:build",
                )
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=f"tmpl:{template_id}"),
                InlineKeyboardButton(text="В главное меню", callback_data="menu:main"),
            ],
        ]
    )
