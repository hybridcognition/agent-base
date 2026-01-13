#!/bin/bash

# Poll for unprocessed Telegram messages and trigger wake-up
# Runs every 5 minutes via cron

WORKSPACE_DIR="/root/workspace"
WAKE_SCRIPT="$WORKSPACE_DIR/scripts/wake-up.sh"
WAKE_LOCK="$WORKSPACE_DIR/.wake-lock"
DB_PATH="$WORKSPACE_DIR/telegram_bot/messages.db"

# Check if agent is already running
if [ -f "$WAKE_LOCK" ]; then
    LOCK_PID=$(cat "$WAKE_LOCK")
    if ps -p "$LOCK_PID" > /dev/null 2>&1; then
        # Agent running, don't interrupt
        exit 0
    fi
fi

# Check for unprocessed messages
if [ -f "$DB_PATH" ]; then
    UNPROCESSED=$(sqlite3 "$DB_PATH" \
        "SELECT COUNT(*) FROM messages WHERE processed = 0 AND direction = 'incoming';" 2>/dev/null)

    if [ -n "$UNPROCESSED" ] && [ "$UNPROCESSED" -gt 0 ]; then
        echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Found $UNPROCESSED unprocessed message(s), triggering wake-up"
        "$WAKE_SCRIPT"
    fi
fi

exit 0
