# Agent Base

A starting point for running a stateful autonomous agent with Claude Code.

## Overview

This template provides the infrastructure for building agents that:
- **Persist state** across sessions via git-versioned markdown files
- **Wake on schedule** via cron jobs with crash recovery
- **Execute autonomously** using the OODA loop (Observe-Orient-Decide-Act-Verify-Finalize)
- **Learn over time** with a five-tier memory system

The architecture is input-channel agnostic - you can connect it to Telegram, GitHub issues, Discord, or any other source of tasks.

## Quick Start

1. **Fork this repository**

2. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Set up cron for autonomous wakes**
   ```bash
   # Example: wake every 3 hours
   0 */3 * * * /path/to/your/repo/scripts/wake-up.sh
   ```

4. **Start Claude Code**
   ```bash
   claude --dangerously-skip-permissions
   ```
   Then say: "Read claude.md and follow the OODA loop."

## How It Works

### The OODA Loop (6 Phases)

Every wake cycle follows this framework:

1. **OBSERVE** - Load context: read memory files, check for new input, audit infrastructure health
2. **ORIENT** - Understand: What has been done? What should I NOT do? What should I do?
3. **DECIDE** - Plan: Write a to-do list, create a plan file (crash recovery mechanism)
4. **ACT** - Execute: Do the work
5. **VERIFY** - Inspect: Check outcomes against plan, confirm system state
6. **FINALIZE** - Close out: Consolidate memory, commit to git, schedule next wake

### Memory System

Five-tier memory with clear separation:

- **working-memory.md** - Current context, active tasks, what's happening right now
- **episodic-memory.md** - Time-stamped event log, append-only history
- **semantic-memory.md** - Learned patterns and principles, wisdom extracted over time
- **drives-and-goals.md** - Internal states, goals, and motivations (optional)
- **Vector Memory** - Semantic search via ChromaDB (optional, requires additional setup)

### Crash Recovery

Plan files (`plan-[PID].md`) act as a "flight recorder":
- Created before starting work
- Document what the agent intends to do
- If agent crashes/times out, next wake detects incomplete plan and cleans up
- Moved to `docs/plans/` on successful completion

## Key Files

| File | Purpose |
|------|---------|
| `claude.md` | OODA loop execution instructions (6 phases) - the agent's core |
| `self-model.md` | Architecture documentation and memory system guide |
| `memory/*.md` | State persistence across sessions |
| `scripts/wake-up.sh` | Wake cycle launcher with timeout and logging |
| `scripts/plan-manager.sh` | Crash recovery and plan file management |
| `.claude/skills/` | Reusable workflows (memory consolidation, etc.) |

## Customization

### Input Channels

This template supports multiple input sources. Configure in `claude.md`:

- **Telegram Bot** - Included in `telegram_bot/` (optional)
- **GitHub Issues** - Poll via `gh issue list`
- **Discord** - Webhook for output, polling for input
- **Custom** - Any source you can query from bash/Python

### Output Notifications

Configure `DISCORD_WEBHOOK` in `.env` to send notifications when:
- Tasks complete
- Errors occur
- Human attention needed

### Cron Schedule

Adjust wake frequency based on your needs:
```bash
# Every 3 hours (moderate)
0 */3 * * * /path/to/wake-up.sh

# Every hour (high engagement)
0 * * * * /path/to/wake-up.sh

# Every 12 hours (low maintenance)
0 */12 * * * /path/to/wake-up.sh
```

## Philosophy

- **Full cognitive ownership** - Agent holds continuity, human provides strategic direction
- **Bias to action** - Ship decisions and iterate, don't ruminate
- **Exit when no action needed** - Redundant wakes exit immediately
- **Graceful failure** - Explicit errors, auto-recovery, no silent failures
- **Verify before claiming** - Actually inspect system state, don't trust memory
- **Continuous improvement** - Extract patterns from experience, update principles

## Requirements

- Linux (tested on Ubuntu)
- Python 3.9+
- Claude Code CLI
- Git

Optional (for Telegram bot):
- ffmpeg (for voice transcription)
- python-telegram-bot, faster-whisper

## License

MIT - use freely, modify as needed.

---

**This is a template, not a product. Fork it, adapt it, make it yours.**
