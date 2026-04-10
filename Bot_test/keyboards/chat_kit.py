from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def chat_kit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Бриф лендинга", callback_data="tmpl:landing_brief"),
                InlineKeyboardButton(text="Оффер", callback_data="tmpl:offer_message"),
            ],
            [
                InlineKeyboardButton(text="ICP", callback_data="tmpl:icp_profile"),
                InlineKeyboardButton(text="Апдейт стартапа", callback_data="tmpl:startup_update"),
            ],
            [
                InlineKeyboardButton(text="Гайд по лендингу", callback_data="useful:landing_page_guide"),
                InlineKeyboardButton(text="Гайд по офферу", callback_data="useful:offer_guide"),
            ],
            [
                InlineKeyboardButton(text="Гайд по ICP", callback_data="useful:icp_guide"),
                InlineKeyboardButton(text="Гайд по апдейту", callback_data="useful:startup_update_guide"),
            ],
            [
                InlineKeyboardButton(text="CAC", callback_data="calc:cac"),
                InlineKeyboardButton(text="LTV", callback_data="calc:ltv"),
                InlineKeyboardButton(text="ROI", callback_data="calc:roi"),
            ],
            [
                InlineKeyboardButton(text="CTR", callback_data="calc:ctr"),
                InlineKeyboardButton(text="CPL", callback_data="calc:cpl"),
                InlineKeyboardButton(text="Runway", callback_data="calc:runway"),
            ],
            [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")],
        ]
    )
