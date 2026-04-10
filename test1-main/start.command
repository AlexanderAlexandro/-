#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8000

cd "$SCRIPT_DIR" || exit 1

echo "Запускаем Currency Flow на http://localhost:$PORT"
echo "Остановка сервера: Ctrl+C"

( sleep 1; open "http://localhost:$PORT" ) >/dev/null 2>&1 &

python3 -m http.server "$PORT" --bind 127.0.0.1
