from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from queue import Empty, Queue
from typing import Any
from urllib.parse import urlparse

from backend.config import Settings, get_settings
from backend.database import build_database
from backend.store import AuthError, MessengerStore, StoreError


class MessengerHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class: type[BaseHTTPRequestHandler],
        settings: Settings,
        store: MessengerStore,
        frontend_dir: Path,
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.settings = settings
        self.store = store
        self.frontend_dir = frontend_dir


class RequestHandler(BaseHTTPRequestHandler):
    server: MessengerHTTPServer
    _CONTENT_SECURITY_POLICY = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "connect-src 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "img-src 'self' data:; "
        "script-src 'self'; "
        "style-src 'self'"
    )

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path in {"/", "/app"}:
                self._handle_page_request(path)
                return

            if path == "/api/health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return

            if path == "/api/auth/me":
                self._handle_auth_me()
                return

            if path == "/api/bootstrap":
                self._handle_bootstrap()
                return

            if path == "/api/events":
                self._handle_events()
                return

            if path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self._send_common_headers(cache_control="no-store")
                self.end_headers()
                return

            self._serve_frontend(path)
        except Exception as error:
            self._handle_unexpected_error(path, error)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        try:
            if not self._ensure_same_origin():
                return

            if path == "/api/auth/register":
                self._handle_register()
                return

            if path == "/api/auth/login":
                self._handle_login()
                return

            if path == "/api/auth/logout":
                self._handle_logout()
                return

            if path == "/api/messages":
                self._handle_create_message()
                return

            if path == "/api/chats/direct":
                self._handle_create_direct_chat()
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Маршрут не найден."})
        except StoreError as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
        except AuthError as error:
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": str(error)})
        except Exception as error:
            self._handle_unexpected_error(path, error)

    def log_message(self, format: str, *args: Any) -> None:
        super().log_message(format, *args)

    def _handle_bootstrap(self) -> None:
        user_id = self._require_user_id()
        if not user_id:
            return

        payload = self.server.store.build_bootstrap(user_id)
        self._send_json(HTTPStatus.OK, payload)

    def _handle_auth_me(self) -> None:
        user_id = self._require_user_id()
        if not user_id:
            return

        payload = {"currentUser": self.server.store.get_public_user(user_id)}
        self._send_json(HTTPStatus.OK, payload)

    def _handle_register(self) -> None:
        body = self._read_json_body()
        user_id = self.server.store.register_user(
            username=body.get("username", ""),
            display_name=body.get("displayName", ""),
            password=body.get("password", ""),
        )
        token = self.server.store.create_session(user_id)
        payload = self.server.store.build_bootstrap(user_id)
        self._send_json(
            HTTPStatus.CREATED,
            payload,
            headers={"Set-Cookie": self._session_cookie(token)},
        )

    def _handle_login(self) -> None:
        body = self._read_json_body()
        user_id = self.server.store.login_user(
            username=body.get("username", ""),
            password=body.get("password", ""),
        )
        token = self.server.store.create_session(user_id)
        payload = self.server.store.build_bootstrap(user_id)
        self._send_json(
            HTTPStatus.OK,
            payload,
            headers={"Set-Cookie": self._session_cookie(token)},
        )

    def _handle_logout(self) -> None:
        token = self._session_token()
        self.server.store.clear_session(token)
        self._send_json(
            HTTPStatus.OK,
            {"success": True},
            headers={"Set-Cookie": self._expired_session_cookie()},
        )

    def _handle_create_message(self) -> None:
        user_id = self._require_user_id()
        if not user_id:
            return

        body = self._read_json_body()
        payload = self.server.store.create_message(
            user_id=user_id,
            chat_id=body.get("chatId", ""),
            text=body.get("text", ""),
        )
        self._send_json(HTTPStatus.CREATED, payload)

    def _handle_create_direct_chat(self) -> None:
        user_id = self._require_user_id()
        if not user_id:
            return

        body = self._read_json_body()
        payload = self.server.store.create_direct_chat(
            user_id=user_id,
            peer_id=body.get("peerId", ""),
        )
        status = HTTPStatus.CREATED if payload["created"] else HTTPStatus.OK
        self._send_json(status, payload)

    def _handle_events(self) -> None:
        user_id = self._require_user_id()
        if not user_id:
            return

        subscriber: Queue = Queue()
        self.server.store.register_stream(user_id, subscriber)

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self._send_common_headers()
        self.end_headers()

        try:
            self._write_sse(
                {
                    "type": "stream.ready",
                    "payload": {"userId": user_id},
                }
            )

            while True:
                try:
                    event = subscriber.get(timeout=15)
                    self._write_sse(event)
                except Empty:
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        finally:
            self.server.store.unregister_stream(user_id, subscriber)

    def _write_sse(self, payload: dict[str, Any]) -> None:
        serialized = json.dumps(payload, ensure_ascii=False)
        self.wfile.write(b"event: app-event\n")
        self.wfile.write(f"data: {serialized}\n\n".encode("utf-8"))
        self.wfile.flush()

    def _read_json_body(self) -> dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise StoreError("Некорректная длина тела запроса.") from error

        if content_length < 0:
            raise StoreError("Некорректная длина тела запроса.")
        if content_length > self.server.settings.request_body_limit_bytes:
            raise StoreError("Запрос слишком большой для MVP API.")

        content_type = self.headers.get("Content-Type", "")
        if content_length and content_type:
            mime_type = content_type.split(";", 1)[0].strip().lower()
            if mime_type != "application/json":
                raise StoreError("API принимает только JSON-запросы.")

        raw = self.rfile.read(content_length) if content_length else b"{}"

        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise StoreError("Некорректный JSON в запросе.") from error

        if not isinstance(payload, dict):
            raise StoreError("Тело запроса должно быть JSON-объектом.")

        return payload

    def _require_user_id(self) -> str | None:
        token = self._session_token()
        user_id = self.server.store.get_user_id_by_session(token)

        if user_id:
            return user_id

        self._send_json(
            HTTPStatus.UNAUTHORIZED,
            {"error": "Сессия не найдена. Выполните вход заново."},
            headers={"Set-Cookie": self._expired_session_cookie()},
        )
        return None

    def _session_token(self) -> str | None:
        raw_cookie = self.headers.get("Cookie", "")
        for cookie_part in raw_cookie.split(";"):
            part = cookie_part.strip()
            if not part or "=" not in part:
                continue
            key, value = part.split("=", 1)
            if key == self.server.settings.cookie_name:
                return value
        return None

    def _session_cookie(self, token: str) -> str:
        secure_part = " Secure;" if self.server.settings.secure_cookies else ""
        return (
            f"{self.server.settings.cookie_name}={token}; "
            f"Path=/; HttpOnly; Max-Age={self.server.settings.session_max_age_seconds};"
            f"{secure_part} SameSite=Lax"
        )

    def _expired_session_cookie(self) -> str:
        secure_part = " Secure;" if self.server.settings.secure_cookies else ""
        return (
            f"{self.server.settings.cookie_name}=; "
            f"Path=/; HttpOnly; Max-Age=0;{secure_part} SameSite=Lax"
        )

    def _handle_page_request(self, path: str) -> None:
        user_id = self.server.store.get_user_id_by_session(self._session_token())

        if path == "/app" and not user_id:
            self._redirect("/")
            return

        if path == "/" and user_id:
            self._redirect("/app")
            return

        self._serve_frontend("/index.html")

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self._send_common_headers(cache_control="no-store")
        self.end_headers()

    def _serve_frontend(self, path: str) -> None:
        file_map = {
            "/": "index.html",
            "/index.html": "index.html",
            "/app.js": "app.js",
            "/styles.css": "styles.css",
        }

        file_name = file_map.get(path)

        if not file_name:
            if path.startswith("/api/"):
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Маршрут не найден."})
                return

            requested_path = (self.server.frontend_dir / path.lstrip("/")).resolve()
            frontend_root = self.server.frontend_dir.resolve()
            if requested_path.is_file() and (
                requested_path == frontend_root or frontend_root in requested_path.parents
            ):
                file_path = requested_path
            else:
                file_path = self.server.frontend_dir / "index.html"
        else:
            file_path = self.server.frontend_dir / file_name

        if not file_path.exists():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Файл не найден."})
            return

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
        }.get(file_path.suffix, "application/octet-stream")

        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self._send_common_headers(cache_control="no-store")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_common_headers(cache_control="no-store")
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_common_headers(self, cache_control: str | None = None) -> None:
        if cache_control:
            self.send_header("Cache-Control", cache_control)
        self.send_header("Content-Security-Policy", self._CONTENT_SECURITY_POLICY)
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def _ensure_same_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True

        parsed_origin = urlparse(origin)
        expected_host = self.headers.get("Host") or f"{self.server.settings.host}:{self.server.settings.port}"
        expected_scheme = "https" if self.server.settings.secure_cookies else "http"

        if parsed_origin.scheme != expected_scheme or parsed_origin.netloc != expected_host:
            self._send_json(
                HTTPStatus.FORBIDDEN,
                {"error": "Запрос с другого origin запрещен."},
            )
            return False

        return True

    def _handle_unexpected_error(self, path: str, error: Exception) -> None:
        self.log_error("Unhandled %s error on %s: %s", self.command, path, error)

        try:
            if path.startswith("/api/"):
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": "Внутренняя ошибка сервера."},
                )
            else:
                body = b"Internal Server Error"
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self._send_common_headers(cache_control="no-store")
                self.end_headers()
                self.wfile.write(body)
        except OSError:
            pass


def run() -> None:
    project_root = Path(__file__).resolve().parent.parent
    settings = get_settings(project_root)
    database = build_database(settings, project_root)
    database.init_schema()
    store = MessengerStore(
        database,
        session_max_age_seconds=settings.session_max_age_seconds,
    )
    frontend_dir = project_root / "frontend"

    server = MessengerHTTPServer(
        (settings.host, settings.port),
        RequestHandler,
        settings,
        store,
        frontend_dir,
    )

    print(
        f"Mini Messenger MVP is running on http://{settings.host}:{settings.port}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMini Messenger MVP stopped.", flush=True)
    finally:
        server.server_close()
