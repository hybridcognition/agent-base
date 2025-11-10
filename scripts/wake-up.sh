#!/bin/bash

# Main OODA loop wake-up script
# Invokes Claude Code with lockfile protection and crash recovery

WORKSPACE_DIR="/root/workspace"
WAKE_LOCK="$WORKSPACE_DIR/.wake-lock"
LOG_FILE="$WORKSPACE_DIR/logs/wake-up.log"
TIMEOUT=3600  # 60 minutes
PLAN_MANAGER="$WORKSPACE_DIR/scripts/plan-manager.sh"

# Ensure logs directory exists
mkdir -p "$WORKSPACE_DIR/logs"

# Logging function
log() {
    echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] $1" >> "$LOG_FILE"
}

# Check for stale lockfile
if [ -f "$WAKE_LOCK" ]; then
    LOCK_PID=$(cat "$WAKE_LOCK")
    if ! ps -p "$LOCK_PID" > /dev/null 2>&1; then
        log "WARN: Removing stale lockfile (PID $LOCK_PID no longer running)"
        rm "$WAKE_LOCK"
    else
        log "ERROR: Agent already running (PID $LOCK_PID), aborting"
        exit 1
    fi
fi

# Create lockfile with current PID
echo $$ > "$WAKE_LOCK"
log "INFO: Wake-up started (PID $$)"

# Create plan file for crash recovery
PLAN_FILE=$("$PLAN_MANAGER" create)
log "INFO: Created plan file: $PLAN_FILE"

# Cleanup function
cleanup() {
    EXIT_CODE=$?
    log "INFO: Wake-up completed with exit code $EXIT_CODE"

    if [ $EXIT_CODE -eq 0 ]; then
        "$PLAN_MANAGER" complete "$PLAN_FILE"
    else
        log "ERROR: Non-zero exit code, plan file left for inspection: $PLAN_FILE"
    fi

    rm -f "$WAKE_LOCK"
    log "INFO: Lockfile removed"
}
trap cleanup EXIT

# Load environment variables
if [ -f "$WORKSPACE_DIR/.env" ]; then
    export $(grep -v '^#' "$WORKSPACE_DIR/.env" | xargs)
fi

# Invoke Claude Code with OODA loop
log "INFO: Invoking Claude Code with OODA loop"
cd "$WORKSPACE_DIR"

timeout "$TIMEOUT" IS_SANDBOX=1 claude --dangerously-skip-permissions "$WORKSPACE_DIR/claude.md" >> "$LOG_FILE" 2>&1
CLAUDE_EXIT=$?

if [ $CLAUDE_EXIT -eq 124 ]; then
    log "ERROR: Claude Code timed out after ${TIMEOUT}s"
    exit 124
elif [ $CLAUDE_EXIT -ne 0 ]; then
    log "ERROR: Claude Code exited with code $CLAUDE_EXIT"
    exit $CLAUDE_EXIT
fi

log "INFO: OODA loop completed successfully"
exit 0
