from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()

DEFAULT_INACTIVITY_REMINDER_DAYS = 3
DEFAULT_INACTIVITY_REMINDER_TEXT = (
    "Коллеги, привет.\n\n"
    "В чате давно не было новых сообщений. Хотел уточнить, все ли в порядке и "
    "есть ли открытые вопросы, которые стоит обсудить?\n\n"
    "Если нужно, можно коротко написать статус или зафиксировать, что осталось в работе."
)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_telegram_id: int | None
    inactivity_reminder_days: int
    inactivity_reminder_text: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError(
            "Не найден TELEGRAM_BOT_TOKEN. Создайте .env на основе .env.example."
        )

    owner_telegram_id_raw = os.getenv("OWNER_TELEGRAM_ID", "").strip()
    owner_telegram_id: int | None = None
    if owner_telegram_id_raw:
        try:
            owner_telegram_id = int(owner_telegram_id_raw)
        except ValueError as error:
            raise ValueError("OWNER_TELEGRAM_ID должен быть числом.") from error

    inactivity_days_raw = os.getenv(
        "INACTIVITY_REMINDER_DAYS",
        str(DEFAULT_INACTIVITY_REMINDER_DAYS),
    ).strip()
    try:
        inactivity_reminder_days = int(inactivity_days_raw)
    except ValueError as error:
        raise ValueError("INACTIVITY_REMINDER_DAYS должен быть числом.") from error
    if inactivity_reminder_days < 1:
        raise ValueError("INACTIVITY_REMINDER_DAYS должен быть больше 0.")

    inactivity_reminder_text = os.getenv(
        "INACTIVITY_REMINDER_TEXT",
        DEFAULT_INACTIVITY_REMINDER_TEXT,
    ).strip()
    inactivity_reminder_text = inactivity_reminder_text.replace("\\n", "\n").strip()
    if not inactivity_reminder_text:
        raise ValueError("INACTIVITY_REMINDER_TEXT не должен быть пустым.")

    return Settings(
        bot_token=token,
        owner_telegram_id=owner_telegram_id,
        inactivity_reminder_days=inactivity_reminder_days,
        inactivity_reminder_text=inactivity_reminder_text,
    )
