#!/bin/bash

# Process Telegram message queue
# Called by bot server or poll-telegram.sh

WORKSPACE_DIR="/root/workspace"
WAKE_LOCK="$WORKSPACE_DIR/.wake-lock"
DB_PATH="$WORKSPACE_DIR/telegram_bot/messages.db"
LOG_FILE="$WORKSPACE_DIR/logs/telegram-process.log"
TIMEOUT=600  # 10 minutes

mkdir -p "$WORKSPACE_DIR/logs"

# Logging function
log() {
    echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] $1" >> "$LOG_FILE"
}

# Check for existing wake lock
if [ -f "$WAKE_LOCK" ]; then
    LOCK_PID=$(cat "$WAKE_LOCK")
    if ps -p "$LOCK_PID" > /dev/null 2>&1; then
        log "Agent already running (PID $LOCK_PID), skipping"
        exit 0
    else
        log "Removing stale wake-lock (PID $LOCK_PID)"
        rm "$WAKE_LOCK"
    fi
fi

# Create wake-lock
echo $$ > "$WAKE_LOCK"
log "Processing Telegram messages (PID $$)"

# Cleanup function
cleanup() {
    EXIT_CODE=$?
    log "Processing completed with exit code $EXIT_CODE"

    # Always release database lock
    if [ -f "$DB_PATH" ]; then
        sqlite3 "$DB_PATH" "UPDATE processing_lock SET is_locked = 0, locked_at = NULL;" 2>/dev/null
    fi

    rm -f "$WAKE_LOCK"
}
trap cleanup EXIT

# Load environment variables
if [ -f "$WORKSPACE_DIR/.env" ]; then
    export $(grep -v '^#' "$WORKSPACE_DIR/.env" | xargs)
fi

# Get unprocessed message count
if [ -f "$DB_PATH" ]; then
    UNPROCESSED=$(sqlite3 "$DB_PATH" \
        "SELECT COUNT(*) FROM messages WHERE processed = 0 AND direction = 'incoming';" 2>/dev/null)

    if [ -z "$UNPROCESSED" ] || [ "$UNPROCESSED" -eq 0 ]; then
        log "No unprocessed messages"
        exit 0
    fi

    log "Found $UNPROCESSED unprocessed message(s)"
fi

# Invoke Claude Code
cd "$WORKSPACE_DIR"
IS_SANDBOX=1 timeout "$TIMEOUT" claude --dangerously-skip-permissions "$WORKSPACE_DIR/claude.md" >> "$LOG_FILE" 2>&1
CLAUDE_EXIT=$?

if [ $CLAUDE_EXIT -eq 124 ]; then
    log "ERROR: Claude timed out after ${TIMEOUT}s"
    exit 124
elif [ $CLAUDE_EXIT -ne 0 ]; then
    log "ERROR: Claude exited with code $CLAUDE_EXIT"
    exit $CLAUDE_EXIT
fi

log "Telegram messages processed successfully"
exit 0
