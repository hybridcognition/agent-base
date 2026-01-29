#!/bin/bash

# Show Telegram bot status
# Usage: ./status.sh

WORKSPACE_DIR="/root/workspace"
DB_PATH="$WORKSPACE_DIR/telegram_bot/messages.db"

echo "=== Telegram Bot Status ==="
echo

# Check if bot process running
if pgrep -f "bot_server.py" > /dev/null; then
    echo "✓ Bot server: RUNNING"
else
    echo "✗ Bot server: NOT RUNNING"
fi

# Check database
if [ -f "$DB_PATH" ]; then
    echo "✓ Database: EXISTS"

    # Show processing lock status
    LOCK_STATUS=$(sqlite3 "$DB_PATH" "SELECT is_locked FROM processing_lock WHERE id = 1;" 2>/dev/null)
    if [ "$LOCK_STATUS" = "1" ]; then
        echo "🔒 Processing lock: LOCKED"
    else
        echo "🔓 Processing lock: UNLOCKED"
    fi

    # Show unprocessed message count
    UNPROCESSED=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM messages WHERE processed = 0 AND direction = 'incoming';" 2>/dev/null)
    echo "📬 Unprocessed messages: $UNPROCESSED"

else
    echo "✗ Database: NOT FOUND"
fi

echo
