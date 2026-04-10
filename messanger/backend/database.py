from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from backend.auth import hash_password
from backend.config import Settings


DEMO_USERS = (
    {
        "username": "alice",
        "display_name": "Alice Johnson",
        "password": "Password123!",
        "salt_hex": "4db8e2058ca6b4d0a7d89a4d2eb7fca1",
        "last_seen_at": "2026-01-12T09:18:00+00:00",
        "created_at": "2026-01-12T09:00:00+00:00",
        "id_hint": "alice",
    },
    {
        "username": "marco",
        "display_name": "Marco Silva",
        "password": "Password123!",
        "salt_hex": "de54fba83dc1fbf639fb55d6fb884e0e",
        "last_seen_at": "2026-01-12T09:18:00+00:00",
        "created_at": "2026-01-12T09:05:00+00:00",
        "id_hint": "marco",
    },
)

DEMO_MESSAGES = (
    {
        "id": "msg_seed_alice_hello",
        "author_username": "alice",
        "body": "Привет! Это стартовый чат для проверки MVP.",
        "created_at": "2026-01-12T09:15:00+00:00",
    },
    {
        "id": "msg_seed_marco_reply",
        "author_username": "marco",
        "body": "Здесь уже работает список чатов, сообщения и realtime-канал.",
        "created_at": "2026-01-12T09:16:00+00:00",
    },
)


class DatabaseManager:
    def __init__(self, db_path: Path, schema_path: Path) -> None:
        self.db_path = db_path
        self.schema_path = schema_path

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(self.db_path), timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def init_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        schema_sql = self.schema_path.read_text(encoding="utf-8")

        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(schema_sql)
            self._ensure_users_last_seen_column(connection)

    def seed_demo_data(self) -> None:
        self.init_schema()

        with self.connect() as connection:
            with connection:
                user_ids_by_username = {
                    user["username"]: self._ensure_demo_user(connection, user)
                    for user in DEMO_USERS
                }
                alice_id = user_ids_by_username["alice"]
                marco_id = user_ids_by_username["marco"]

                chat_id = self._ensure_direct_chat(
                    connection,
                    alice_id,
                    marco_id,
                    created_at="2026-01-12T09:10:00+00:00",
                )

                for message in DEMO_MESSAGES:
                    self._ensure_message(
                        connection,
                        message_id=message["id"],
                        chat_id=chat_id,
                        author_id=user_ids_by_username[message["author_username"]],
                        body=message["body"],
                        created_at=message["created_at"],
                    )

                self._refresh_chat_timestamp(connection, chat_id)

    def _ensure_demo_user(
        self,
        connection: sqlite3.Connection,
        user: dict[str, str],
    ) -> str:
        user_id = f"user_seed_{user['id_hint']}"
        salt_hex, password_hash = hash_password(
            user["password"],
            bytes.fromhex(user["salt_hex"]),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO users (
                id,
                username,
                display_name,
                password_salt,
                password_hash,
                last_seen_at,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user["username"],
                user["display_name"],
                salt_hex,
                password_hash,
                user.get("last_seen_at"),
                user["created_at"],
                user["created_at"],
            ),
        )
        persisted_user = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (user["username"],),
        ).fetchone()

        if not persisted_user:
            raise RuntimeError(f"Could not ensure demo user {user['username']}.")

        return str(persisted_user["id"])

    def _ensure_direct_chat(
        self,
        connection: sqlite3.Connection,
        first_user_id: str,
        second_user_id: str,
        created_at: str | None = None,
    ) -> str:
        pair_key = self._direct_pair_key(first_user_id, second_user_id)
        chat_id = f"chat_seed_{pair_key.replace(':', '_')}"
        timestamp = created_at or self._now()
        connection.execute(
            """
            INSERT OR IGNORE INTO chats (
                id,
                type,
                title,
                direct_pair_key,
                created_at,
                updated_at
            )
            VALUES (?, 'direct', NULL, ?, ?, ?)
            """,
            (chat_id, pair_key, timestamp, timestamp),
        )

        persisted_chat = connection.execute(
            "SELECT id FROM chats WHERE direct_pair_key = ?",
            (pair_key,),
        ).fetchone()

        if not persisted_chat:
            raise RuntimeError("Could not ensure seeded direct chat.")

        chat_id = str(persisted_chat["id"])

        joined_at = created_at or self._now()
        connection.executemany(
            """
            INSERT OR IGNORE INTO chat_members (
                chat_id,
                user_id,
                role,
                joined_at
            )
            VALUES (?, ?, 'member', ?)
            """,
            (
                (chat_id, first_user_id, joined_at),
                (chat_id, second_user_id, joined_at),
            ),
        )
        return chat_id

    def _ensure_message(
        self,
        connection: sqlite3.Connection,
        message_id: str,
        chat_id: str,
        author_id: str,
        body: str,
        created_at: str,
    ) -> None:
        connection.execute(
            """
            INSERT OR IGNORE INTO messages (
                id,
                chat_id,
                author_id,
                body,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (message_id, chat_id, author_id, body, created_at, created_at),
        )

    def _refresh_chat_timestamp(self, connection: sqlite3.Connection, chat_id: str) -> None:
        connection.execute(
            """
            UPDATE chats
            SET updated_at = COALESCE(
                (
                    SELECT MAX(created_at)
                    FROM messages
                    WHERE chat_id = chats.id
                ),
                chats.updated_at
            )
            WHERE id = ?
            """,
            (chat_id,),
        )

    def _direct_pair_key(self, first_user_id: str, second_user_id: str) -> str:
        return ":".join(sorted((first_user_id, second_user_id)))

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _ensure_users_last_seen_column(self, connection: sqlite3.Connection) -> None:
        columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }

        if "last_seen_at" in columns:
            return

        connection.execute("ALTER TABLE users ADD COLUMN last_seen_at TEXT")


def build_database(settings: Settings, project_root: Path) -> DatabaseManager:
    return DatabaseManager(
        db_path=settings.database_path,
        schema_path=project_root / "backend" / "sql" / "schema.sql",
    )
