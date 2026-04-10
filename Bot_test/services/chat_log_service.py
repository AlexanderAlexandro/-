from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from aiogram.enums import ChatType, ContentType
from aiogram.types import Chat, Message, User


BASE_DIR = Path(__file__).resolve().parent.parent
RUNTIME_DIR = BASE_DIR / "runtime"
LOGS_DIR = RUNTIME_DIR / "chat_logs"
REGISTRY_FILE = RUNTIME_DIR / "known_chats.json"
INACTIVITY_DAYS = 3
DECISION_KEYWORDS = (
    "решили",
    "договорились",
    "утвердили",
    "утверждаем",
    "делаем",
    "беру",
    "берем",
    "запускаем",
    "запускаю",
    "фиксирую",
)
BLOCKER_KEYWORDS = (
    "блокер",
    "проблема",
    "не получается",
    "не могу",
    "непонятно",
    "застрял",
    "нужна помощь",
    "нужен фидбэк",
    "мешает",
)
ACTION_KEYWORDS = (
    "сделаю",
    "сделаем",
    "подготовлю",
    "запущу",
    "проверю",
    "скину",
    "обновлю",
    "доработаю",
    "возьму",
    "беру",
)
QUESTION_KEYWORDS = (
    "кто ",
    "что ",
    "где ",
    "когда ",
    "почему ",
    "зачем ",
    "как ",
    "нужно ли",
    "есть ли",
    "можем ли",
)


@dataclass(frozen=True)
class KnownChat:
    chat_id: int
    title: str
    chat_type: str
    registered_at: datetime | None
    last_message_at: datetime | None
    last_inactivity_reminder_at: datetime | None
    inactivity_reminders_enabled: bool


@dataclass(frozen=True)
class ChatAnalytics:
    chat_title: str
    days: int
    messages_count: int
    participants_count: int
    questions_count: int
    links_count: int
    decisions_count: int
    blockers_count: int
    actions_count: int
    score: int
    health_label: str
    recommendation: str
    top_participants: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ChatSignals:
    chat_title: str
    days: int
    questions: tuple[str, ...]
    decisions: tuple[str, ...]
    blockers: tuple[str, ...]
    actions: tuple[str, ...]


def _ensure_storage() -> None:
    RUNTIME_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)


def _local_dt(value: datetime) -> datetime:
    return value.astimezone()


def _serialize_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    return _local_dt(value).isoformat()


def _deserialize_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _deserialize_bool(value: object, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


def _load_registry() -> dict[str, dict[str, object]]:
    _ensure_storage()
    if not REGISTRY_FILE.exists():
        return {}
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def _save_registry(data: dict[str, dict[str, object]]) -> None:
    _ensure_storage()
    REGISTRY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _day_file_path(chat_id: int, value: datetime) -> Path:
    local_dt = _local_dt(value)
    day_dir = LOGS_DIR / local_dt.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    return day_dir / f"{chat_id}.jsonl"


def _read_day_records(chat_id: int, day_value: datetime) -> list[dict[str, str]]:
    file_path = _day_file_path(chat_id, day_value)
    if not file_path.exists():
        return []

    day_label = _local_dt(day_value).strftime("%Y-%m-%d")
    records: list[dict[str, str]] = []
    with file_path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            payload = json.loads(raw_line)
            records.append(
                {
                    "day": day_label,
                    "timestamp": str(payload["timestamp"]),
                    "sender": str(payload["sender"]),
                    "text": str(payload["text"]),
                }
            )
    return records


def _chat_title(chat: Chat) -> str:
    if chat.title:
        return chat.title
    if chat.full_name:
        return chat.full_name
    return str(chat.id)


def _user_name(user: User | None) -> str:
    if user is None:
        return "Unknown"
    full_name = " ".join(part for part in [user.first_name, user.last_name] if part).strip()
    if user.username:
        return f"{full_name} (@{user.username})" if full_name else f"@{user.username}"
    return full_name or str(user.id)


def _sender_name(message: Message) -> str:
    if message.from_user:
        return _user_name(message.from_user)
    if message.sender_chat:
        return message.sender_chat.title or str(message.sender_chat.id)
    return "Unknown"


def _content_label(message: Message) -> str:
    labels = {
        ContentType.PHOTO: "[Фото]",
        ContentType.VIDEO: "[Видео]",
        ContentType.VOICE: "[Голосовое сообщение]",
        ContentType.VIDEO_NOTE: "[Кружок]",
        ContentType.DOCUMENT: "[Документ]",
        ContentType.STICKER: "[Стикер]",
        ContentType.AUDIO: "[Аудио]",
        ContentType.ANIMATION: "[GIF]",
        ContentType.LOCATION: "[Локация]",
        ContentType.CONTACT: "[Контакт]",
        ContentType.POLL: "[Опрос]",
    }
    return labels.get(message.content_type, f"[{message.content_type}]")


def _normalize_signal_text(value: str, *, limit: int = 160) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 1].rstrip()}…"


def _contains_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(keyword in normalized for keyword in keywords)


def _is_question_text(text: str) -> bool:
    normalized = " ".join(text.lower().split())
    return "?" in normalized or any(normalized.startswith(keyword) for keyword in QUESTION_KEYWORDS)


def _recent_records(
    chat_id: int,
    *,
    days: int,
    now: datetime | None = None,
) -> list[dict[str, str]]:
    current_time = _local_dt(now or datetime.now().astimezone())
    records: list[dict[str, str]] = []
    for offset in range(days - 1, -1, -1):
        day_value = current_time - timedelta(days=offset)
        records.extend(_read_day_records(chat_id, day_value))
    return records


def _chat_score(
    *,
    messages_count: int,
    participants_count: int,
    decisions_count: int,
    blockers_count: int,
    actions_count: int,
) -> int:
    score = 20
    score += min(messages_count * 2, 25)
    score += min(participants_count * 4, 20)
    score += min(decisions_count * 5, 15)
    score += min(actions_count * 4, 10)
    score -= min(blockers_count * 3, 15)
    return max(0, min(100, score))


def _chat_health_label(score: int) -> str:
    if score >= 75:
        return "сильный рабочий ритм"
    if score >= 55:
        return "стабильный рабочий ритм"
    if score >= 35:
        return "средний ритм, нужен фокус"
    return "чату нужен явный фокус"


def _chat_recommendation(
    *,
    questions_count: int,
    decisions_count: int,
    blockers_count: int,
    actions_count: int,
) -> str:
    if blockers_count > decisions_count:
        return (
            "Блокеров и неясностей сейчас больше, чем зафиксированных решений. "
            "Полезно быстро выделить владельцев и снять 1-2 главных стоп-фактора."
        )
    if questions_count > 0 and decisions_count == 0:
        return (
            "В чате есть вопросы, но почти не видно явных решений. "
            "Стоит коротко зафиксировать договоренности отдельным сообщением."
        )
    if actions_count >= 3 and decisions_count >= 2:
        return (
            "Чат выглядит рабочим: есть не только обсуждение, но и признаки решений и действий. "
            "Полезно продолжать фиксировать следующий шаг и владельца."
        )
    return (
        "Обсуждение идет, но полезно чаще фиксировать решения, следующие шаги и ответственных, "
        "чтобы чат не превращался только в поток идей."
    )


def _signal_samples(
    records: list[dict[str, str]],
    predicate,
    *,
    limit: int = 3,
) -> tuple[str, ...]:
    results: list[str] = []
    for record in reversed(records):
        if not predicate(record["text"]):
            continue
        results.append(
            f"[{record['day']} {record['timestamp']}] {record['sender']}: {_normalize_signal_text(record['text'])}"
        )
        if len(results) >= limit:
            break
    return tuple(results)


def _link_messages_count(records: list[dict[str, str]]) -> int:
    markers = ("http://", "https://", "www.", "t.me/")
    return sum(1 for record in records if any(marker in record["text"].lower() for marker in markers))


def _question_messages_count(records: list[dict[str, str]]) -> int:
    return sum(1 for record in records if _is_question_text(record["text"]))


def analyze_chat_activity(
    chat_id: int,
    *,
    days: int = 3,
    now: datetime | None = None,
) -> ChatAnalytics:
    known_chat = get_known_chat(chat_id)
    chat_title = known_chat.title if known_chat else str(chat_id)
    records = _recent_records(chat_id, days=days, now=now)

    participants = Counter(record["sender"] for record in records)
    messages_count = len(records)
    questions_count = _question_messages_count(records)
    links_count = _link_messages_count(records)
    decisions_count = sum(
        1 for record in records if _contains_keyword(record["text"], DECISION_KEYWORDS)
    )
    blockers_count = sum(
        1 for record in records if _contains_keyword(record["text"], BLOCKER_KEYWORDS)
    )
    actions_count = sum(
        1 for record in records if _contains_keyword(record["text"], ACTION_KEYWORDS)
    )
    score = _chat_score(
        messages_count=messages_count,
        participants_count=len(participants),
        decisions_count=decisions_count,
        blockers_count=blockers_count,
        actions_count=actions_count,
    )
    recommendation = (
        "За выбранный период бот не увидел новых сообщений. Если чат живой, проверьте, "
        "что у бота есть доступ к сообщениям и он добавлен в нужную группу."
        if not records
        else _chat_recommendation(
            questions_count=questions_count,
            decisions_count=decisions_count,
            blockers_count=blockers_count,
            actions_count=actions_count,
        )
    )

    return ChatAnalytics(
        chat_title=chat_title,
        days=days,
        messages_count=messages_count,
        participants_count=len(participants),
        questions_count=questions_count,
        links_count=links_count,
        decisions_count=decisions_count,
        blockers_count=blockers_count,
        actions_count=actions_count,
        score=score,
        health_label=_chat_health_label(score),
        recommendation=recommendation,
        top_participants=tuple(participants.most_common(5)),
    )


def collect_chat_signals(
    chat_id: int,
    *,
    days: int = 3,
    now: datetime | None = None,
) -> ChatSignals:
    known_chat = get_known_chat(chat_id)
    chat_title = known_chat.title if known_chat else str(chat_id)
    records = _recent_records(chat_id, days=days, now=now)

    return ChatSignals(
        chat_title=chat_title,
        days=days,
        questions=_signal_samples(
            records,
            _is_question_text,
        ),
        decisions=_signal_samples(
            records,
            lambda value: _contains_keyword(value, DECISION_KEYWORDS),
        ),
        blockers=_signal_samples(
            records,
            lambda value: _contains_keyword(value, BLOCKER_KEYWORDS),
        ),
        actions=_signal_samples(
            records,
            lambda value: _contains_keyword(value, ACTION_KEYWORDS),
        ),
    )


def extract_message_text(message: Message) -> str:
    if message.text:
        return message.text
    if message.caption:
        return f"{_content_label(message)} {message.caption}"
    return _content_label(message)


def register_chat(chat: Chat, registered_at: datetime | None = None) -> None:
    if chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    now = _local_dt(registered_at or datetime.now().astimezone())
    data = _load_registry()
    existing = data.get(str(chat.id), {})

    data[str(chat.id)] = {
        "chat_id": chat.id,
        "title": _chat_title(chat),
        "chat_type": str(chat.type),
        "registered_at": existing.get("registered_at") or _serialize_dt(now),
        "last_message_at": existing.get("last_message_at"),
        "last_inactivity_reminder_at": existing.get("last_inactivity_reminder_at"),
        "inactivity_reminders_enabled": _deserialize_bool(
            existing.get("inactivity_reminders_enabled"),
            default=True,
        ),
    }
    _save_registry(data)


def mark_chat_activity(chat: Chat, activity_at: datetime) -> None:
    if chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    register_chat(chat, registered_at=activity_at)
    data = _load_registry()
    payload = data[str(chat.id)]
    payload["title"] = _chat_title(chat)
    payload["chat_type"] = str(chat.type)
    payload["last_message_at"] = _serialize_dt(activity_at)
    # После любого нового сообщения разрешаем напоминание заново, если снова наступит тишина.
    payload["last_inactivity_reminder_at"] = None
    _save_registry(data)


def mark_inactivity_reminder_sent(chat_id: int, sent_at: datetime | None = None) -> None:
    data = _load_registry()
    payload = data.get(str(chat_id))
    if payload is None:
        return

    payload["last_inactivity_reminder_at"] = _serialize_dt(sent_at or datetime.now().astimezone())
    _save_registry(data)


def set_inactivity_reminders_enabled(chat_id: int, enabled: bool) -> KnownChat | None:
    data = _load_registry()
    payload = data.get(str(chat_id))
    if payload is None:
        return None

    payload["inactivity_reminders_enabled"] = enabled
    if enabled:
        # После ручного включения разрешаем следующую проверку тишины без дополнительной активности.
        payload["last_inactivity_reminder_at"] = None
    _save_registry(data)
    return get_known_chat(chat_id)


def log_group_message(message: Message) -> None:
    if message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    if message.from_user and message.from_user.is_bot:
        return

    mark_chat_activity(message.chat, message.date)
    file_path = _day_file_path(message.chat.id, message.date)
    record = {
        "timestamp": _local_dt(message.date).strftime("%H:%M"),
        "sender": _sender_name(message),
        "text": extract_message_text(message),
    }
    with file_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def _to_known_chat(chat_id: str, payload: dict[str, object]) -> KnownChat:
    return KnownChat(
        chat_id=int(chat_id),
        title=str(payload.get("title") or chat_id),
        chat_type=str(payload.get("chat_type") or "group"),
        registered_at=_deserialize_dt(payload.get("registered_at")),  # type: ignore[arg-type]
        last_message_at=_deserialize_dt(payload.get("last_message_at")),  # type: ignore[arg-type]
        last_inactivity_reminder_at=_deserialize_dt(payload.get("last_inactivity_reminder_at")),  # type: ignore[arg-type]
        inactivity_reminders_enabled=_deserialize_bool(
            payload.get("inactivity_reminders_enabled"),
            default=True,
        ),
    )


def list_known_chats() -> tuple[KnownChat, ...]:
    raw = _load_registry()
    chats = [_to_known_chat(chat_id, payload) for chat_id, payload in raw.items()]
    return tuple(sorted(chats, key=lambda item: item.title.lower()))


def get_known_chat(chat_id: int) -> KnownChat | None:
    return next((chat for chat in list_known_chats() if chat.chat_id == chat_id), None)


def get_inactive_chats(
    *,
    now: datetime | None = None,
    inactivity_days: int = INACTIVITY_DAYS,
) -> tuple[KnownChat, ...]:
    current_time = _local_dt(now or datetime.now().astimezone())
    inactivity_border = current_time - timedelta(days=inactivity_days)
    inactive_chats: list[KnownChat] = []

    for chat in list_known_chats():
        baseline = chat.last_message_at or chat.registered_at
        if baseline is None:
            continue
        if not chat.inactivity_reminders_enabled:
            continue
        if baseline > inactivity_border:
            continue
        if chat.last_inactivity_reminder_at is not None:
            continue
        inactive_chats.append(chat)

    return tuple(inactive_chats)


def build_today_history(chat_id: int) -> tuple[str, str]:
    known_chat = get_known_chat(chat_id)
    title = known_chat.title if known_chat else str(chat_id)

    today_path = _day_file_path(chat_id, datetime.now().astimezone())
    if not today_path.exists():
        return title, "За сегодня сохраненных сообщений пока нет."

    lines: list[str] = []
    with today_path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            payload = json.loads(raw_line)
            lines.append(f"[{payload['timestamp']}] {payload['sender']}: {payload['text']}")

    if not lines:
        return title, "За сегодня сохраненных сообщений пока нет."

    return title, "\n".join(lines)
