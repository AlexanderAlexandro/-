from __future__ import annotations

from collections.abc import Awaitable, Callable


StopCallback = Callable[[], Awaitable[None]]

_stop_callback: StopCallback | None = None


def register_stop_callback(callback: StopCallback) -> None:
    global _stop_callback
    _stop_callback = callback


def clear_stop_callback() -> None:
    global _stop_callback
    _stop_callback = None


async def request_stop() -> bool:
    if _stop_callback is None:
        return False

    await _stop_callback()
    return True
