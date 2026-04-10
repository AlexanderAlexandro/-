from __future__ import annotations

import hashlib
import hmac
import re
import secrets


USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
DISPLAY_NAME_MIN_LENGTH = 2
DISPLAY_NAME_MAX_LENGTH = 30
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64
PASSWORD_HASH_ITERATIONS = 120_000


def normalize_username(username: str) -> str:
    return username.strip().lower()


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt_bytes = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PASSWORD_HASH_ITERATIONS,
    )
    return salt_bytes.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, password_hash: str) -> bool:
    if not salt_hex or not password_hash:
        return False

    try:
        salt = bytes.fromhex(salt_hex)
        _, candidate_hash = hash_password(password, salt)
    except (TypeError, ValueError):
        return False

    return hmac.compare_digest(candidate_hash, password_hash)


def get_registration_validation_error(
    username: str,
    display_name: str,
    password: str,
) -> str | None:
    if not USERNAME_RE.match(username):
        return "Логин должен быть 3-20 символов и состоять из букв, цифр или _."
    if len(display_name) < DISPLAY_NAME_MIN_LENGTH or len(display_name) > DISPLAY_NAME_MAX_LENGTH:
        return (
            f"Имя должно быть длиной от {DISPLAY_NAME_MIN_LENGTH} "
            f"до {DISPLAY_NAME_MAX_LENGTH} символов."
        )
    return get_password_validation_error(password)


def get_login_validation_error(username: str, password: str) -> str | None:
    if not username:
        return "Введите логин."
    if not password:
        return "Введите пароль."
    return None


def get_password_validation_error(password: str) -> str | None:
    if password != password.strip():
        return "Пароль не должен начинаться или заканчиваться пробелом."
    if len(password) < PASSWORD_MIN_LENGTH or len(password) > PASSWORD_MAX_LENGTH:
        return (
            f"Пароль должен быть длиной от {PASSWORD_MIN_LENGTH} "
            f"до {PASSWORD_MAX_LENGTH} символов."
        )
    return None
