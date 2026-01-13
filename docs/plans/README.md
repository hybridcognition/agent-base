# Completed Plans

This folder contains archived plan files from successfully completed wake cycles.

## Plan File Lifecycle

1. **Created** in root directory at start of OODA loop: `plan-[PID].md`
2. **Updated** during DECIDE and ACT phases with intentions and progress
3. **Moved here** on successful completion via `plan-manager.sh complete`
4. **Left in root** if agent crashes (enables recovery by next wake)

## Why Keep Completed Plans?

- **Audit trail** - What was attempted and completed
- **Pattern detection** - Identify recurring task types
- **Debug reference** - Understand past decisions
- **Progress evidence** - Track agent activity over time

## Cleanup

Old plans can be archived or deleted periodically:
```bash
# Archive plans older than 30 days
find docs/plans/ -name "plan-*.md" -mtime +30 -exec mv {} docs/plans/archive/ \;
```

## Not Required

Keeping all plans is optional. You can:
- Delete after a week
- Keep only the most recent N plans
- Archive to a separate storage

The important thing is that **incomplete plans in root = crash indicator**.
