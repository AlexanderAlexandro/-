from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, ChatMemberUpdated, Message

from config import get_settings
from keyboards.admin import (
    admin_back_keyboard,
    admin_menu_keyboard,
    admin_section_back_keyboard,
    known_chats_keyboard,
    reminder_chat_keyboard,
    reminder_chats_keyboard,
)
from services.chat_log_service import (
    analyze_chat_activity,
    build_today_history,
    collect_chat_signals,
    get_known_chat,
    list_known_chats,
    register_chat,
    set_inactivity_reminders_enabled,
)
from services.runtime_control import request_stop
from utils.text import escape_html
from utils.messages import safe_edit_text
from utils.states import AdminBroadcastState


router = Router()


def _is_owner(message_or_callback: Message | CallbackQuery) -> bool:
    settings = get_settings()
    owner_id = settings.owner_telegram_id
    if owner_id is None:
        return False

    user = (
        message_or_callback.from_user
        if isinstance(message_or_callback, CallbackQuery)
        else message_or_callback.from_user
    )
    return user is not None and user.id == owner_id


def _admin_only_text() -> str:
    return "Этот раздел доступен только владельцу бота."


def _admin_menu_text() -> str:
    return "<b>Панель владельца</b>\n\nВыберите действие."


def _history_text_for_chat(chat_id: int) -> tuple[str, str]:
    chat_title, history_text = build_today_history(chat_id)
    header = f"История за сегодня\nЧат: {chat_title}\n\n"
    return chat_title, header + history_text


def _list_lines(items: tuple[str, ...], *, empty_text: str) -> str:
    if not items:
        return f"• {escape_html(empty_text)}"
    return "\n".join(f"• {escape_html(item)}" for item in items)


def _top_participants_text(items: tuple[tuple[str, int], ...]) -> str:
    if not items:
        return "• Пока нет данных по участникам."
    return "\n".join(
        f"• {escape_html(name)} — {count} сообщ."
        for name, count in items
    )


def _analytics_text(chat_id: int) -> str:
    analytics = analyze_chat_activity(chat_id, days=3)
    return (
        "<b>📊 Оценка чата</b>\n\n"
        f"Чат: {escape_html(analytics.chat_title)}\n"
        f"Период: последние {analytics.days} суток\n"
        f"Индекс чата: <b>{analytics.score}/100</b>\n"
        f"Статус: {escape_html(analytics.health_label)}\n\n"
        "<b>Снимок активности</b>\n"
        f"• Сообщений: {analytics.messages_count}\n"
        f"• Участников: {analytics.participants_count}\n"
        f"• Вопросов: {analytics.questions_count}\n"
        f"• Сообщений со ссылками: {analytics.links_count}\n"
        f"• Решений: {analytics.decisions_count}\n"
        f"• Блокеров: {analytics.blockers_count}\n"
        f"• Следующих шагов: {analytics.actions_count}\n\n"
        "<b>Кто держит ритм</b>\n"
        f"{_top_participants_text(analytics.top_participants)}\n\n"
        "<b>Что это значит</b>\n"
        f"{escape_html(analytics.recommendation)}"
    )


def _signals_text(chat_id: int) -> str:
    signals = collect_chat_signals(chat_id, days=3)
    return (
        "<b>🧭 Сигналы чата</b>\n\n"
        f"Чат: {escape_html(signals.chat_title)}\n"
        f"Период: последние {signals.days} суток\n\n"
        "<b>Вопросы</b>\n"
        f"{_list_lines(signals.questions, empty_text='Явных вопросов за период не нашел.')}\n\n"
        "<b>Решения</b>\n"
        f"{_list_lines(signals.decisions, empty_text='Явных договоренностей пока не видно.')}\n\n"
        "<b>Блокеры</b>\n"
        f"{_list_lines(signals.blockers, empty_text='Явных блокеров бот не заметил.')}\n\n"
        "<b>Следующие шаги</b>\n"
        f"{_list_lines(signals.actions, empty_text='Зафиксированных действий пока мало.')}"
    )


def _reminder_status_label(enabled: bool) -> str:
    return "включены" if enabled else "выключены"


def _reminder_chat_text(chat_id: int) -> str:
    known_chat = get_known_chat(chat_id)
    if known_chat is None:
        return "<b>Автонапоминания</b>\n\nЧат не найден."

    settings = get_settings()
    return (
        "<b>Автонапоминания</b>\n\n"
        f"Чат: {known_chat.title}\n"
        f"Статус: {_reminder_status_label(known_chat.inactivity_reminders_enabled)}\n\n"
        "Если напоминания включены, бот раз в час проверяет тишину и пишет в чат, "
        f"когда в нем нет новых человеческих сообщений дольше {settings.inactivity_reminder_days} суток."
    )


@router.my_chat_member()
async def register_chat_on_join(event: ChatMemberUpdated) -> None:
    if event.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    if event.new_chat_member.status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
    }:
        register_chat(event.chat)


@router.message(Command("admin"), F.chat.type == ChatType.PRIVATE)
async def open_admin_menu(message: Message, state: FSMContext) -> None:
    if not _is_owner(message):
        return

    await state.clear()
    await message.answer(_admin_menu_text(), reply_markup=admin_menu_keyboard())


@router.message(Command("shutdown"), F.chat.type == ChatType.PRIVATE)
async def shutdown_bot_command(message: Message, state: FSMContext) -> None:
    if not _is_owner(message):
        return

    await state.clear()
    await message.answer(
        (
            "<b>Остановка бота</b>\n\n"
            "Текущий процесс будет остановлен. Чтобы запустить бота снова, "
            "нужно вручную выполнить <code>python main.py</code> на компьютере."
        )
    )
    await request_stop()


@router.callback_query(F.data == "admin:menu")
async def admin_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    await safe_edit_text(
        callback,
        _admin_menu_text(),
        reply_markup=admin_menu_keyboard(),
    )


@router.callback_query(F.data == "admin:analytics")
async def admin_analytics_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chats = list_known_chats()
    if not chats:
        await safe_edit_text(
            callback,
            "<b>Оценка чата</b>\n\nПока нет известных чатов для анализа.",
            reply_markup=admin_back_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        (
            "<b>Оценка чата</b>\n\n"
            "Выберите чат. Бот покажет индекс активности, сигналы по решениям и короткую рекомендацию."
        ),
        reply_markup=known_chats_keyboard("analytics", chats),
    )


@router.callback_query(F.data == "admin:signals")
async def admin_signals_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chats = list_known_chats()
    if not chats:
        await safe_edit_text(
            callback,
            "<b>Сигналы чата</b>\n\nПока нет известных чатов для анализа.",
            reply_markup=admin_back_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        (
            "<b>Сигналы чата</b>\n\n"
            "Выберите чат. Я покажу последние вопросы, решения, блокеры и следующие шаги, которые видны в переписке."
        ),
        reply_markup=known_chats_keyboard("signals", chats),
    )


@router.callback_query(F.data == "admin:history")
async def admin_history_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chats = list_known_chats()
    if not chats:
        await safe_edit_text(
            callback,
            "<b>История за сегодня</b>\n\nПока нет известных чатов с сохраненными сообщениями.",
            reply_markup=admin_back_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        "<b>История за сегодня</b>\n\nВыберите чат.",
        reply_markup=known_chats_keyboard("history", chats),
    )


@router.callback_query(F.data == "admin:send")
async def admin_send_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chats = list_known_chats()
    if not chats:
        await safe_edit_text(
            callback,
            "<b>Отправка сообщения</b>\n\nПока нет известных чатов для отправки.",
            reply_markup=admin_back_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        "<b>Отправка сообщения</b>\n\nВыберите чат, куда бот должен отправить сообщение.",
        reply_markup=known_chats_keyboard("send", chats),
    )


@router.callback_query(F.data == "admin:reminders")
async def admin_reminders_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chats = list_known_chats()
    if not chats:
        await safe_edit_text(
            callback,
            "<b>Автонапоминания</b>\n\nПока нет известных чатов для настройки.",
            reply_markup=admin_back_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        "<b>Автонапоминания</b>\n\nВыберите чат, для которого хотите изменить настройки.",
        reply_markup=reminder_chats_keyboard(chats),
    )


@router.callback_query(F.data.startswith("adminchat:reminders:view:"))
async def reminder_chat_details(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chat_id = int(callback.data.split(":")[3])
    known_chat = get_known_chat(chat_id)
    if known_chat is None:
        await safe_edit_text(
            callback,
            "<b>Автонапоминания</b>\n\nЧат не найден.",
            reply_markup=admin_back_keyboard(),
        )
        return

    await safe_edit_text(
        callback,
        _reminder_chat_text(chat_id),
        reply_markup=reminder_chat_keyboard(
            chat_id,
            enabled=known_chat.inactivity_reminders_enabled,
        ),
    )


@router.callback_query(F.data.startswith("adminchat:reminders:toggle:"))
async def toggle_reminder_for_chat(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chat_id = int(callback.data.split(":")[3])
    known_chat = get_known_chat(chat_id)
    if known_chat is None:
        await callback.answer("Чат не найден.", show_alert=True)
        return

    updated_chat = set_inactivity_reminders_enabled(
        chat_id,
        enabled=not known_chat.inactivity_reminders_enabled,
    )
    await safe_edit_text(
        callback,
        _reminder_chat_text(chat_id),
        reply_markup=reminder_chat_keyboard(
            chat_id,
            enabled=updated_chat.inactivity_reminders_enabled if updated_chat else False,
        ),
    )


@router.callback_query(F.data.startswith("adminchat:analytics:"))
async def show_chat_analytics(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chat_id = int(callback.data.split(":")[2])
    await safe_edit_text(
        callback,
        _analytics_text(chat_id),
        reply_markup=admin_section_back_keyboard("admin:analytics"),
    )


@router.callback_query(F.data.startswith("adminchat:signals:"))
async def show_chat_signals(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chat_id = int(callback.data.split(":")[2])
    await safe_edit_text(
        callback,
        _signals_text(chat_id),
        reply_markup=admin_section_back_keyboard("admin:signals"),
    )


@router.callback_query(F.data.startswith("adminchat:history:"))
async def send_today_history(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    await state.clear()
    chat_id = int(callback.data.split(":")[2])
    chat_title, full_text = _history_text_for_chat(chat_id)
    history_html = escape_html(full_text)

    if len(history_html) <= 3900:
        await safe_edit_text(
            callback,
            f"<pre>{history_html}</pre>",
            reply_markup=admin_section_back_keyboard("admin:history"),
        )
        return

    document = BufferedInputFile(
        full_text.encode("utf-8"),
        filename=f"history_{chat_id}.txt",
    )
    if callback.message is not None:
        await callback.message.answer_document(
            document,
            caption=(
                f"История чата «{chat_title}» за сегодня не поместилась в одно сообщение, "
                "поэтому отправляю TXT-файлом."
            ),
            reply_markup=admin_section_back_keyboard("admin:history"),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("adminchat:send:"))
async def prepare_send_to_chat(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_owner(callback):
        await callback.answer(_admin_only_text(), show_alert=True)
        return

    chat_id = int(callback.data.split(":")[2])
    known_chat = get_known_chat(chat_id)
    await state.set_state(AdminBroadcastState.awaiting_text)
    await state.set_data({"target_chat_id": chat_id})

    await safe_edit_text(
        callback,
        (
            "<b>Отправка сообщения</b>\n\n"
            f"Целевой чат: {known_chat.title if known_chat else chat_id}\n\n"
            "Теперь отправьте в этот личный чат любое сообщение. Бот скопирует его в выбранный чат от своего имени."
        ),
        reply_markup=admin_back_keyboard(),
    )


@router.message(AdminBroadcastState.awaiting_text, F.chat.type == ChatType.PRIVATE)
async def send_message_to_selected_chat(message: Message, state: FSMContext) -> None:
    if not _is_owner(message):
        await state.clear()
        return

    data = await state.get_data()
    target_chat_id = data["target_chat_id"]
    known_chat = get_known_chat(target_chat_id)

    await message.copy_to(target_chat_id)
    await state.clear()
    await message.answer(
        (
            "<b>Готово</b>\n\n"
            f"Сообщение отправлено в чат: {known_chat.title if known_chat else target_chat_id}"
        ),
        reply_markup=admin_menu_keyboard(),
    )
