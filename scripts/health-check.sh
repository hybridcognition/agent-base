#!/bin/bash

# System health monitoring with auto-recovery
# Runs every 15 minutes via cron
# Checks for stale locks and auto-recovers

WORKSPACE_DIR="/root/workspace"
LOG_FILE="$WORKSPACE_DIR/logs/health-check.log"
WAKE_LOCK="$WORKSPACE_DIR/.wake-lock"
DB_PATH="$WORKSPACE_DIR/telegram_bot/messages.db"
STALE_THRESHOLD=900  # 15 minutes in seconds

mkdir -p "$WORKSPACE_DIR/logs"

# Logging function
log() {
    echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] $1" | tee -a "$LOG_FILE"
}

log "=== Health check starting ==="

# Check 1: Stale wake-lock
if [ -f "$WAKE_LOCK" ]; then
    LOCK_PID=$(cat "$WAKE_LOCK")
    if ! ps -p "$LOCK_PID" > /dev/null 2>&1; then
        log "RECOVERY: Removing stale wake-lock (PID $LOCK_PID not running)"
        rm "$WAKE_LOCK"
    else
        # Check how long process has been running
        PROCESS_AGE=$(ps -o etimes= -p "$LOCK_PID" 2>/dev/null)
        if [ -n "$PROCESS_AGE" ] && [ "$PROCESS_AGE" -gt 3600 ]; then
            log "WARN: Agent process running for ${PROCESS_AGE}s (>60 min), may be hung"
        fi
    fi
fi

# Check 2: Stale database lock
if [ -f "$DB_PATH" ]; then
    LOCK_INFO=$(sqlite3 "$DB_PATH" \
        "SELECT locked_at FROM processing_lock WHERE is_locked = 1;" 2>/dev/null)

    if [ -n "$LOCK_INFO" ]; then
        # Calculate lock age
        LOCKED_AT=$(date -d "$LOCK_INFO" +%s 2>/dev/null)
        NOW=$(date +%s)

        if [ -n "$LOCKED_AT" ]; then
            LOCK_AGE=$((NOW - LOCKED_AT))

            if [ "$LOCK_AGE" -gt "$STALE_THRESHOLD" ]; then
                log "RECOVERY: Releasing stale database lock (age: ${LOCK_AGE}s)"
                sqlite3 "$DB_PATH" "UPDATE processing_lock SET is_locked = 0, locked_at = NULL;"
            fi
        fi
    fi
fi

# Check 3: High message queue depth
if [ -f "$DB_PATH" ]; then
    QUEUE_DEPTH=$(sqlite3 "$DB_PATH" \
        "SELECT COUNT(*) FROM messages WHERE processed = 0 AND direction = 'incoming';" 2>/dev/null)

    if [ -n "$QUEUE_DEPTH" ] && [ "$QUEUE_DEPTH" -gt 5 ]; then
        log "WARN: High message queue depth: $QUEUE_DEPTH unprocessed messages"
    fi
fi

# Check 4: Incomplete plan files
"$WORKSPACE_DIR/scripts/plan-manager.sh" check-incomplete >> "$LOG_FILE" 2>&1

log "=== Health check complete ==="
exit 0
