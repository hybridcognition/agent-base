#!/bin/bash

# Plan file management for crash recovery
# Commands: create, complete <file>, check-incomplete

WORKSPACE_DIR="/root/workspace"
PLANS_DIR="$WORKSPACE_DIR/docs/plans"

mkdir -p "$PLANS_DIR"

case "$1" in
    create)
        # Create new plan file with PID
        PLAN_FILE="$WORKSPACE_DIR/plan-$$.md"
        cat > "$PLAN_FILE" <<EOF
# Wake-Up Plan #$$

**Started**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**PID**: $$

## Observation Phase


## Orient Phase


## Decision Phase


## Actions Taken

EOF
        echo "$PLAN_FILE"
        ;;

    complete)
        # Move completed plan to archive
        if [ -z "$2" ]; then
            echo "ERROR: Plan file path required" >&2
            exit 1
        fi

        PLAN_FILE="$2"
        if [ ! -f "$PLAN_FILE" ]; then
            echo "ERROR: Plan file not found: $PLAN_FILE" >&2
            exit 1
        fi

        # Add completion timestamp
        echo "" >> "$PLAN_FILE"
        echo "**Completed**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" >> "$PLAN_FILE"

        # Move to archive
        BASENAME=$(basename "$PLAN_FILE")
        mv "$PLAN_FILE" "$PLANS_DIR/"
        echo "Plan archived: $PLANS_DIR/$BASENAME"
        ;;

    check-incomplete)
        # Find incomplete plan files (= crashed agent)
        INCOMPLETE=$(find "$WORKSPACE_DIR" -maxdepth 1 -name "plan-*.md" -type f)

        if [ -n "$INCOMPLETE" ]; then
            echo "WARNING: Incomplete plan files detected (agent crashed):" >&2
            echo "$INCOMPLETE" >&2
            exit 1
        fi

        echo "No incomplete plan files found"
        exit 0
        ;;

    *)
        echo "Usage: $0 {create|complete <plan-file>|check-incomplete}" >&2
        exit 1
        ;;
esac
