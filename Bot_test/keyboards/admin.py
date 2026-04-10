from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.chat_log_service import KnownChat


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="История за сегодня", callback_data="admin:history")],
            [InlineKeyboardButton(text="Оценка чата", callback_data="admin:analytics")],
            [InlineKeyboardButton(text="Сигналы чата", callback_data="admin:signals")],
            [InlineKeyboardButton(text="Отправить сообщение в чат", callback_data="admin:send")],
            [InlineKeyboardButton(text="Автонапоминания", callback_data="admin:reminders")],
            [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")],
        ]
    )


def known_chats_keyboard(action: str, chats: tuple[KnownChat, ...]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=chat.title,
                callback_data=f"adminchat:{action}:{chat.chat_id}",
            )
        ]
        for chat in chats
    ]
    rows.append([InlineKeyboardButton(text="Назад", callback_data="admin:menu")])
    rows.append([InlineKeyboardButton(text="В главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="admin:menu")],
            [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")],
        ]
    )


def admin_section_back_keyboard(
    section_callback: str,
    section_label: str = "К списку чатов",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=section_label, callback_data=section_callback)],
            [InlineKeyboardButton(text="В панель владельца", callback_data="admin:menu")],
            [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")],
        ]
    )


def reminder_chats_keyboard(chats: tuple[KnownChat, ...]) -> InlineKeyboardMarkup:
    rows = []
    for chat in chats:
        status = "вкл" if chat.inactivity_reminders_enabled else "выкл"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{chat.title} [{status}]",
                    callback_data=f"adminchat:reminders:view:{chat.chat_id}",
                )
            ]
        )

    rows.append([InlineKeyboardButton(text="Назад", callback_data="admin:menu")])
    rows.append([InlineKeyboardButton(text="В главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reminder_chat_keyboard(chat_id: int, enabled: bool) -> InlineKeyboardMarkup:
    toggle_text = "Выключить напоминания" if enabled else "Включить напоминания"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=f"adminchat:reminders:toggle:{chat_id}",
                )
            ],
            [InlineKeyboardButton(text="К списку чатов", callback_data="admin:reminders")],
            [InlineKeyboardButton(text="В главное меню", callback_data="menu:main")],
        ]
    )
