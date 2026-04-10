from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8000
    env: str = "development"
    database_path: Path = Path("data/messenger.sqlite3")
    cookie_name: str = "mini_messenger_session"
    session_max_age_seconds: int = 86_400
    request_body_limit_bytes: int = 16_384
    secure_cookies: bool = False


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def get_settings(project_root: Path) -> Settings:
    env_values = load_dotenv(project_root / ".env")

    host = os.getenv("APP_HOST") or env_values.get("APP_HOST") or "127.0.0.1"
    port_value = os.getenv("APP_PORT") or env_values.get("APP_PORT") or "8000"
    env = os.getenv("APP_ENV") or env_values.get("APP_ENV") or "development"
    raw_database_path = (
        os.getenv("APP_DB_PATH")
        or env_values.get("APP_DB_PATH")
        or "data/messenger.sqlite3"
    )
    session_max_age_value = (
        os.getenv("APP_SESSION_MAX_AGE_SECONDS")
        or env_values.get("APP_SESSION_MAX_AGE_SECONDS")
        or "86400"
    )
    request_body_limit_value = (
        os.getenv("APP_REQUEST_BODY_LIMIT_BYTES")
        or env_values.get("APP_REQUEST_BODY_LIMIT_BYTES")
        or "16384"
    )

    try:
        port = int(port_value)
    except ValueError:
        port = 8000
    if port <= 0 or port > 65_535:
        port = 8000

    try:
        session_max_age_seconds = int(session_max_age_value)
    except ValueError:
        session_max_age_seconds = 86_400
    if session_max_age_seconds <= 0:
        session_max_age_seconds = 86_400

    try:
        request_body_limit_bytes = int(request_body_limit_value)
    except ValueError:
        request_body_limit_bytes = 16_384
    if request_body_limit_bytes <= 0:
        request_body_limit_bytes = 16_384

    secure_cookies = env.lower() == "production"
    database_path = Path(raw_database_path)
    if not database_path.is_absolute():
        database_path = project_root / database_path

    return Settings(
        host=host,
        port=port,
        env=env,
        database_path=database_path,
        session_max_age_seconds=session_max_age_seconds,
        request_body_limit_bytes=request_body_limit_bytes,
        secure_cookies=secure_cookies,
    )
