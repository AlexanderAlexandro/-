from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from queue import Queue
import sqlite3
import secrets
from threading import RLock
from time import time
from typing import Any
from uuid import uuid4

from backend.auth import (
    get_login_validation_error,
    get_registration_validation_error,
    hash_password,
    normalize_username,
    verify_password,
)
from backend.database import DatabaseManager


class StoreError(ValueError):
    """Raised when user input or state is invalid."""


class AuthError(PermissionError):
    """Raised when authentication fails."""


@dataclass(frozen=True)
class SessionRecord:
    user_id: str
    expires_at: float


class MessengerStore:
    def __init__(
        self,
        database: DatabaseManager,
        session_max_age_seconds: int = 86_400,
    ) -> None:
        self._database = database
        self._lock = RLock()
        self._session_max_age_seconds = max(1, int(session_max_age_seconds))
        self._sessions: dict[str, SessionRecord] = {}
        self._subscribers: dict[str, set[Queue]] = defaultdict(set)
        self._online_counts: dict[str, int] = defaultdict(int)

    def get_user_id_by_session(self, token: str | None) -> str | None:
        if not token:
            return None

        with self._lock:
            now = time()
            self._prune_expired_sessions(now)
            session = self._sessions.get(token)
            if not session:
                return None
            return session.user_id

    def get_public_user(self, user_id: str) -> dict[str, Any]:
        with self._database.connect() as connection:
            user_row = connection.execute(
                """
                SELECT id, username, display_name, last_seen_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

        if not user_row:
            raise AuthError("Пользователь не найден.")

        return self._serialize_user(user_row)

    def create_session(self, user_id: str) -> str:
        token = secrets.token_urlsafe(24)
        expires_at = time() + self._session_max_age_seconds

        with self._lock:
            self._prune_expired_sessions(time())
            self._sessions[token] = SessionRecord(user_id=user_id, expires_at=expires_at)

        return token

    def clear_session(self, token: str | None) -> None:
        if not token:
            return

        with self._lock:
            self._sessions.pop(token, None)

    def register_user(self, username: str, display_name: str, password: str) -> str:
        normalized_username = normalize_username(username)
        normalized_display_name = display_name.strip()

        validation_error = get_registration_validation_error(
            username=normalized_username,
            display_name=normalized_display_name,
            password=password,
        )
        if validation_error:
            raise StoreError(validation_error)

        user_id = self._generate_id("user")
        created_at = self._now()
        password_salt, password_hash = hash_password(password)

        try:
            with self._database.connect() as connection:
                with connection:
                    existing = connection.execute(
                        "SELECT id FROM users WHERE username = ?",
                        (normalized_username,),
                    ).fetchone()
                    if existing:
                        raise StoreError("Пользователь с таким логином уже существует.")

                    connection.execute(
                        """
                        INSERT INTO users (
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
                            normalized_username,
                            normalized_display_name,
                            password_salt,
                            password_hash,
                            None,
                            created_at,
                            created_at,
                        ),
                    )
        except sqlite3.IntegrityError as error:
            raise StoreError("Не удалось сохранить пользователя. Попробуйте еще раз.") from error

        return user_id

    def login_user(self, username: str, password: str) -> str:
        normalized_username = normalize_username(username)

        validation_error = get_login_validation_error(
            username=normalized_username,
            password=password,
        )
        if validation_error:
            raise StoreError(validation_error)

        with self._database.connect() as connection:
            user_row = connection.execute(
                """
                SELECT id, password_salt, password_hash
                FROM users
                WHERE username = ?
                """,
                (normalized_username,),
            ).fetchone()

        if not user_row:
            raise AuthError("Неверный логин или пароль.")

        if not verify_password(
            password=password,
            salt_hex=str(user_row["password_salt"]),
            password_hash=str(user_row["password_hash"]),
        ):
            raise AuthError("Неверный логин или пароль.")

        return str(user_row["id"])

    def build_bootstrap(self, user_id: str) -> dict[str, Any]:
        with self._database.connect() as connection:
            user_row = connection.execute(
                """
                SELECT id, username, display_name, last_seen_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
            if not user_row:
                raise AuthError("Пользователь не найден.")

            chat_payloads = self._fetch_chat_summaries(connection, user_id)
            messages_by_chat = {
                chat["id"]: self._fetch_messages_for_chat(connection, chat["id"])
                for chat in chat_payloads
            }
            directory_users = self._fetch_directory_users(connection, user_id)

        return {
            "currentUser": self._serialize_user(user_row),
            "chats": chat_payloads,
            "messagesByChat": messages_by_chat,
            "users": directory_users,
        }

    def create_direct_chat(self, user_id: str, peer_id: str) -> dict[str, Any]:
        normalized_peer_id = str(peer_id).strip()

        if not normalized_peer_id:
            raise StoreError("Выберите пользователя для нового диалога.")

        if normalized_peer_id == user_id:
            raise StoreError("Нельзя создать диалог с самим собой.")

        with self._database.connect() as connection:
            with connection:
                peer_row = connection.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE id = ?
                    """,
                    (normalized_peer_id,),
                ).fetchone()

                if not peer_row:
                    raise StoreError("Пользователь не найден.")

                existing_chat_id = self._find_direct_chat_id(
                    connection,
                    user_id,
                    normalized_peer_id,
                )
                created = existing_chat_id is None
                chat_id = existing_chat_id or self._ensure_direct_chat(
                    connection,
                    user_id,
                    normalized_peer_id,
                )
                chat_payload = self._fetch_chat_summary(connection, chat_id, user_id)
                messages = self._fetch_messages_for_chat(connection, chat_id)

        return {
            "created": created,
            "chatId": chat_id,
            "chat": chat_payload,
            "messages": messages,
        }

    def create_message(self, user_id: str, chat_id: str, text: str) -> dict[str, Any]:
        normalized_chat_id = str(chat_id).strip()
        normalized_text = text.strip()

        if not normalized_chat_id:
            raise StoreError("Чат не найден.")
        if not normalized_text:
            raise StoreError("Сообщение не должно быть пустым.")
        if len(normalized_text) > 500:
            raise StoreError("Сообщение не должно быть длиннее 500 символов.")

        message_id = self._generate_id("msg")
        created_at = self._now()

        with self._database.connect() as connection:
            with connection:
                membership = connection.execute(
                    """
                    SELECT c.id
                    FROM chats c
                    JOIN chat_members cm
                        ON cm.chat_id = c.id
                    WHERE c.id = ? AND cm.user_id = ?
                    """,
                    (normalized_chat_id, user_id),
                ).fetchone()

                if not membership:
                    raise StoreError("Чат не найден.")

                connection.execute(
                    """
                    INSERT INTO messages (
                        id,
                        chat_id,
                        author_id,
                        body,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message_id,
                        normalized_chat_id,
                        user_id,
                        normalized_text,
                        created_at,
                        created_at,
                    ),
                )

                serialized_message = {
                    "id": message_id,
                    "chatId": normalized_chat_id,
                    "authorId": user_id,
                    "text": normalized_text,
                    "createdAt": created_at,
                }
                recipient_rows = connection.execute(
                    """
                    SELECT user_id
                    FROM chat_members
                    WHERE chat_id = ?
                    """,
                    (normalized_chat_id,),
                ).fetchall()
                recipient_ids = [str(row["user_id"]) for row in recipient_rows]

                sender_payload = {
                    "chatId": normalized_chat_id,
                    "chat": self._fetch_chat_summary(connection, normalized_chat_id, user_id),
                    "message": serialized_message,
                }
                recipient_payloads = [
                    (
                        recipient_id,
                        {
                            "chatId": normalized_chat_id,
                            "chat": self._fetch_chat_summary(
                                connection,
                                normalized_chat_id,
                                recipient_id,
                            ),
                            "message": serialized_message,
                        },
                    )
                    for recipient_id in recipient_ids
                    if recipient_id != user_id
                ]

        self._publish([user_id], "message.created", sender_payload)

        for recipient_id, payload in recipient_payloads:
            self._publish([recipient_id], "message.created", payload)

        return sender_payload

    def register_stream(self, user_id: str, subscriber: Queue) -> None:
        with self._lock:
            self._subscribers[user_id].add(subscriber)
            self._online_counts[user_id] += 1
            became_online = self._online_counts[user_id] == 1

        if became_online:
            self._broadcast_presence(user_id, True, self._get_last_seen_at(user_id))

    def unregister_stream(self, user_id: str, subscriber: Queue) -> None:
        with self._lock:
            subscribers = self._subscribers.get(user_id)
            if subscribers:
                subscribers.discard(subscriber)
                if not subscribers:
                    self._subscribers.pop(user_id, None)

            online_count = self._online_counts.get(user_id, 0)
            if online_count > 0:
                online_count -= 1

            if online_count > 0:
                self._online_counts[user_id] = online_count
            else:
                self._online_counts.pop(user_id, None)

            became_offline = online_count == 0

        if became_offline:
            last_seen_at = self._now()
            self._set_last_seen_at(user_id, last_seen_at)
            self._broadcast_presence(user_id, False, last_seen_at)

    def _fetch_chat_summaries(
        self,
        connection: sqlite3.Connection,
        viewer_id: str,
    ) -> list[dict[str, Any]]:
        chat_rows = connection.execute(
            """
            SELECT
                c.id,
                c.type,
                c.title,
                c.updated_at,
                peer.id AS peer_id,
                peer.username AS peer_username,
                peer.display_name AS peer_display_name,
                peer.last_seen_at AS peer_last_seen_at,
                last_message.id AS last_message_id,
                last_message.author_id AS last_message_author_id,
                last_message.body AS last_message_body,
                last_message.created_at AS last_message_created_at
            FROM chats c
            JOIN chat_members viewer_member
                ON viewer_member.chat_id = c.id
               AND viewer_member.user_id = ?
            LEFT JOIN chat_members peer_member
                ON peer_member.chat_id = c.id
               AND peer_member.user_id != ?
               AND c.type = 'direct'
            LEFT JOIN users peer
                ON peer.id = peer_member.user_id
            LEFT JOIN messages last_message
                ON last_message.id = (
                    SELECT m.id
                    FROM messages m
                    WHERE m.chat_id = c.id
                    ORDER BY m.created_at DESC, m.id DESC
                    LIMIT 1
                )
            ORDER BY c.updated_at DESC, c.id DESC
            """,
            (viewer_id, viewer_id),
        ).fetchall()

        return [self._serialize_chat_row(row) for row in chat_rows]

    def _fetch_directory_users(
        self,
        connection: sqlite3.Connection,
        viewer_id: str,
    ) -> list[dict[str, Any]]:
        rows = connection.execute(
            """
            SELECT id, username, display_name, last_seen_at
            FROM users
            WHERE id != ?
            ORDER BY display_name COLLATE NOCASE ASC, username COLLATE NOCASE ASC
            """,
            (viewer_id,),
        ).fetchall()
        return [self._serialize_user(row) for row in rows]

    def _fetch_chat_summary(
        self,
        connection: sqlite3.Connection,
        chat_id: str,
        viewer_id: str,
    ) -> dict[str, Any]:
        row = connection.execute(
            """
            SELECT
                c.id,
                c.type,
                c.title,
                c.updated_at,
                peer.id AS peer_id,
                peer.username AS peer_username,
                peer.display_name AS peer_display_name,
                peer.last_seen_at AS peer_last_seen_at,
                last_message.id AS last_message_id,
                last_message.author_id AS last_message_author_id,
                last_message.body AS last_message_body,
                last_message.created_at AS last_message_created_at
            FROM chats c
            JOIN chat_members viewer_member
                ON viewer_member.chat_id = c.id
               AND viewer_member.user_id = ?
            LEFT JOIN chat_members peer_member
                ON peer_member.chat_id = c.id
               AND peer_member.user_id != ?
               AND c.type = 'direct'
            LEFT JOIN users peer
                ON peer.id = peer_member.user_id
            LEFT JOIN messages last_message
                ON last_message.id = (
                    SELECT m.id
                    FROM messages m
                    WHERE m.chat_id = c.id
                    ORDER BY m.created_at DESC, m.id DESC
                    LIMIT 1
                )
            WHERE c.id = ?
            """,
            (viewer_id, viewer_id, chat_id),
        ).fetchone()

        if not row:
            raise StoreError("Чат не найден.")

        return self._serialize_chat_row(row)

    def _fetch_messages_for_chat(
        self,
        connection: sqlite3.Connection,
        chat_id: str,
    ) -> list[dict[str, Any]]:
        rows = connection.execute(
            """
            SELECT id, chat_id, author_id, body, created_at
            FROM messages
            WHERE chat_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (chat_id,),
        ).fetchall()
        return [self._serialize_message(row) for row in rows]

    def _serialize_user(self, row: sqlite3.Row) -> dict[str, Any]:
        user_id = str(row["id"])
        return {
            "id": user_id,
            "username": str(row["username"]),
            "displayName": str(row["display_name"]),
            "online": self._is_user_online(user_id),
            "lastSeenAt": str(row["last_seen_at"]) if row["last_seen_at"] else None,
        }

    def _serialize_message(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": str(row["id"]),
            "chatId": str(row["chat_id"]),
            "authorId": str(row["author_id"]),
            "text": str(row["body"]),
            "createdAt": str(row["created_at"]),
        }

    def _serialize_chat_row(self, row: sqlite3.Row) -> dict[str, Any]:
        if row["peer_id"]:
            peer_id = str(row["peer_id"])
            peer_payload = {
                "id": peer_id,
                "username": str(row["peer_username"]),
                "displayName": str(row["peer_display_name"]),
                "online": self._is_user_online(peer_id),
                "lastSeenAt": str(row["peer_last_seen_at"]) if row["peer_last_seen_at"] else None,
            }
        else:
            peer_payload = {
                "id": str(row["id"]),
                "username": "group",
                "displayName": str(row["title"] or "Group chat"),
                "online": False,
                "lastSeenAt": None,
            }

        last_message = None
        if row["last_message_id"]:
            last_message = {
                "id": str(row["last_message_id"]),
                "chatId": str(row["id"]),
                "authorId": str(row["last_message_author_id"]),
                "text": str(row["last_message_body"]),
                "createdAt": str(row["last_message_created_at"]),
            }

        return {
            "id": str(row["id"]),
            "peer": peer_payload,
            "updatedAt": str(row["updated_at"]),
            "lastMessage": last_message,
        }

    def _ensure_direct_chat(
        self,
        connection: sqlite3.Connection,
        first_user_id: str,
        second_user_id: str,
    ) -> str:
        existing_chat_id = self._find_direct_chat_id(connection, first_user_id, second_user_id)
        if existing_chat_id:
            return existing_chat_id

        pair_key = self._direct_pair_key(first_user_id, second_user_id)
        chat_id = self._generate_id("chat")
        created_at = self._now()

        try:
            connection.execute(
                """
                INSERT INTO chats (
                    id,
                    type,
                    title,
                    direct_pair_key,
                    created_at,
                    updated_at
                )
                VALUES (?, 'direct', NULL, ?, ?, ?)
                """,
                (chat_id, pair_key, created_at, created_at),
            )
        except sqlite3.IntegrityError:
            persisted_chat_id = self._find_direct_chat_id(connection, first_user_id, second_user_id)
            if persisted_chat_id:
                return persisted_chat_id
            raise

        connection.executemany(
            """
            INSERT INTO chat_members (
                chat_id,
                user_id,
                role,
                joined_at
            )
            VALUES (?, ?, 'member', ?)
            """,
            (
                (chat_id, first_user_id, created_at),
                (chat_id, second_user_id, created_at),
            ),
        )
        return chat_id

    def _find_direct_chat_id(
        self,
        connection: sqlite3.Connection,
        first_user_id: str,
        second_user_id: str,
    ) -> str | None:
        pair_key = self._direct_pair_key(first_user_id, second_user_id)
        row = connection.execute(
            "SELECT id FROM chats WHERE direct_pair_key = ?",
            (pair_key,),
        ).fetchone()
        return str(row["id"]) if row else None

    def _publish(self, recipient_ids: list[str], event_type: str, payload: dict[str, Any]) -> None:
        event = {"type": event_type, "payload": payload}

        with self._lock:
            queues: list[Queue] = []
            for user_id in set(recipient_ids):
                queues.extend(list(self._subscribers.get(user_id, set())))

        for queue in queues:
            queue.put_nowait(event)

    def _broadcast_presence(self, user_id: str, online: bool, last_seen_at: str | None) -> None:
        event = {
            "type": "presence.updated",
            "payload": {
                "userId": user_id,
                "online": online,
                "lastSeenAt": last_seen_at,
            },
        }

        with self._lock:
            queues = [
                subscriber
                for subscribers in self._subscribers.values()
                for subscriber in list(subscribers)
            ]

        for queue in queues:
            queue.put_nowait(event)

    def _direct_pair_key(self, first_user_id: str, second_user_id: str) -> str:
        return ":".join(sorted((first_user_id, second_user_id)))

    def _is_user_online(self, user_id: str) -> bool:
        with self._lock:
            return self._online_counts.get(user_id, 0) > 0

    def _prune_expired_sessions(self, now: float) -> None:
        expired_tokens = [
            token
            for token, session in self._sessions.items()
            if session.expires_at <= now
        ]

        for token in expired_tokens:
            self._sessions.pop(token, None)

    def _get_last_seen_at(self, user_id: str) -> str | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT last_seen_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

        if not row or not row["last_seen_at"]:
            return None

        return str(row["last_seen_at"])

    def _set_last_seen_at(self, user_id: str, value: str) -> None:
        with self._database.connect() as connection:
            with connection:
                connection.execute(
                    """
                    UPDATE users
                    SET last_seen_at = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (value, self._now(), user_id),
                )

    def _generate_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:12]}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
