#!/bin/bash

# Start the Telegram bot server
# Usage: ./start_bot.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/root/workspace"

# Load environment variables
if [ -f "$WORKSPACE_DIR/.env" ]; then
    export $(grep -v '^#' "$WORKSPACE_DIR/.env" | xargs)
fi

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Initialize database
python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR/src'); from database import init_db; init_db('$WORKSPACE_DIR/telegram_bot/messages.db')"

# Start bot
echo "Starting Telegram bot..."
cd "$SCRIPT_DIR"
python3 src/bot_server.py
