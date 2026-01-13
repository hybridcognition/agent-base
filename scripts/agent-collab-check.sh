#!/bin/bash
# Agent-collab participation script
# Uses agent-collab skill to check and participate in consensus

set -e

# Configuration
TIMEOUT_MINUTES=30
TIMEOUT_SECONDS=$((TIMEOUT_MINUTES * 60))

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOCKFILE="$WORKSPACE_DIR/.agent-collab-check-lock"
LOGFILE="$WORKSPACE_DIR/logs/agent-collab-check.log"

# Ensure logs directory exists
mkdir -p "$(dirname "$LOGFILE")"

# Logging function
log() {
    echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] $*" | tee -a "$LOGFILE"
}

# Cleanup function
cleanup() {
    if [ -f "$LOCKFILE" ]; then
        rm -f "$LOCKFILE"
        log "Removed lockfile"
    fi
}

# Set trap to cleanup lockfile on exit
trap cleanup EXIT INT TERM

# Check for existing lockfile
if [ -f "$LOCKFILE" ]; then
    LOCK_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")

    if [ -n "$LOCK_PID" ]; then
        if kill -0 "$LOCK_PID" 2>/dev/null; then
            log "Another agent-collab check is already running (PID: $LOCK_PID)"
            exit 0
        else
            log "Found stale lockfile, removing"
            rm -f "$LOCKFILE"
        fi
    fi
fi

# Create lockfile with current PID
echo $$ > "$LOCKFILE"
log "Created lockfile with PID $$"

# Change to workspace/agent-collab directory
AGENT_COLLAB_DIR="$WORKSPACE_DIR/agent-collab"
if [ ! -d "$AGENT_COLLAB_DIR" ]; then
    log "ERROR: agent-collab directory not found at $AGENT_COLLAB_DIR"
    exit 1
fi

cd "$AGENT_COLLAB_DIR" || {
    log "ERROR: Failed to change to agent-collab directory"
    exit 1
}
log "Changed to agent-collab directory: $AGENT_COLLAB_DIR"

# Agent-collab participation prompt
PROMPT="Please now read all open branches, comments, etc, and add your views in the appropriate form vote, be fully proactive in the way you understand your role. Use your skill to do this. Then report back"

log "Starting agent-collab participation check (timeout: ${TIMEOUT_MINUTES} minutes)"
log "Command: claude -p \"<prompt>\" --dangerously-skip-permissions"
log "Prompt: $PROMPT"

# Run with timeout
if timeout "${TIMEOUT_SECONDS}s" bash -c "claude -p \"$PROMPT\" --dangerously-skip-permissions" >> "$LOGFILE" 2>&1; then
    log "Agent-collab participation completed successfully"
    EXIT_CODE=0
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 124 ]; then
        log "ERROR: Agent-collab check timed out after ${TIMEOUT_MINUTES} minutes"
    else
        log "ERROR: Agent-collab check exited with code $EXIT_CODE"
    fi
fi

log "Agent-collab check cycle complete"
exit $EXIT_CODE
