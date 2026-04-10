#!/bin/zsh

set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$HOME/.telegram_utility_bot"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
AGENT_LABEL="com.bot_test.telegram_utility_bot"
AGENT_FILE="$LAUNCH_AGENTS_DIR/$AGENT_LABEL.plist"

if [[ ! -f "$SOURCE_DIR/.env" ]]; then
    echo "Не найден $SOURCE_DIR/.env. Сначала создайте и заполните .env." >&2
    exit 1
fi

if [[ ! -x "$SOURCE_DIR/.venv/bin/python" ]]; then
    echo "Не найдено виртуальное окружение в $SOURCE_DIR/.venv." >&2
    echo "Сначала установите зависимости через pip install -r requirements.txt" >&2
    exit 1
fi

mkdir -p "$LAUNCH_AGENTS_DIR"
mkdir -p "$DEPLOY_DIR"

rsync -a --delete \
    --exclude '.git/' \
    --exclude '.pycache/' \
    --exclude '__pycache__/' \
    --exclude 'runtime/' \
    "$SOURCE_DIR/" "$DEPLOY_DIR/"

mkdir -p "$DEPLOY_DIR/runtime"
mkdir -p "$DEPLOY_DIR/runtime/chat_logs"
chmod +x "$DEPLOY_DIR/scripts/run_bot.sh"

# Один раз переносим уже накопленные данные чатов из исходного проекта,
# если в фоновой копии они еще не появились.
if [[ ! -f "$DEPLOY_DIR/runtime/known_chats.json" && -f "$SOURCE_DIR/runtime/known_chats.json" ]]; then
    cp "$SOURCE_DIR/runtime/known_chats.json" "$DEPLOY_DIR/runtime/known_chats.json"
fi

if [[ -d "$SOURCE_DIR/runtime/chat_logs" ]]; then
    rsync -a "$SOURCE_DIR/runtime/chat_logs/" "$DEPLOY_DIR/runtime/chat_logs/"
fi

"$DEPLOY_DIR/.venv/bin/python" -c "import aiogram" >/dev/null

: > "$DEPLOY_DIR/runtime/launchd.stdout.log"
: > "$DEPLOY_DIR/runtime/launchd.stderr.log"

cat > "$AGENT_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$AGENT_LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>$DEPLOY_DIR/.venv/bin/python</string>
        <string>$DEPLOY_DIR/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$DEPLOY_DIR</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$DEPLOY_DIR/runtime/launchd.stdout.log</string>

    <key>StandardErrorPath</key>
    <string>$DEPLOY_DIR/runtime/launchd.stderr.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$AGENT_FILE" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$AGENT_FILE"
launchctl kickstart -k "gui/$(id -u)/$AGENT_LABEL"

echo
echo "Готово. Фоновый запуск включен."
echo "Рабочая копия сервиса:"
echo "$DEPLOY_DIR"
echo
echo "Проверить статус:"
echo "launchctl print gui/$(id -u)/$AGENT_LABEL"
echo
echo "Логи:"
echo "tail -f $DEPLOY_DIR/runtime/launchd.stdout.log"
echo "tail -f $DEPLOY_DIR/runtime/launchd.stderr.log"
