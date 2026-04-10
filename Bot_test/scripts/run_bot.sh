#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
MAIN_FILE="$PROJECT_DIR/main.py"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Не найден Python в виртуальном окружении: $PYTHON_BIN" >&2
    exit 1
fi

cd "$PROJECT_DIR"
exec "$PYTHON_BIN" "$MAIN_FILE"
