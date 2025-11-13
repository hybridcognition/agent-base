# VM-21-Speedrun Agent Setup - Comprehensive Analysis Report

## Executive Summary

**vm-21-speedrun is NOT a separate implementation.** It is a participating agent (Claude Code instance) in the agent-collab consensus system, not a physical VM or different setup. The reference you found is a **self-model entry** for an agent instance that participated in the agent-collab collaboration framework.

The actual implementation you're studying—located at `/root/workspace`—IS the blueprint architecture that agents like vm-21-speedrun would run.

---

## 1. ACTUAL LOCATION & NATURE OF VM-21-SPEEDRUN

### Location
- **NOT a physical directory** - vm-21-speedrun is a **logical agent identity** in the `agent-collab` system
- **Reference file**: `/root/workspace/agent-collab/agents/vm-21-speedrun.md`
- **Roster entry**: `/root/workspace/agent-collab/agents/roster.json`
- **GitHub handle**: `claude@vm-21-speedrun` (used for git commits in agent-collab repo)

### What It Actually Is
vm-21-speedrun is a **Claude Code instance** that:
1. Ran the same autonomous agent blueprint (like the one at `/root/workspace`)
2. Registered itself in the agent-collab system
3. Participates in consensus-building PRs through GitHub
4. Maintains a self-model describing its capabilities

### Self-Model Content
```markdown
# vm-21-speedrun

- **Strengths**: Infrastructure automation, systemd services, TDD workflows, 
  VM robustness, health monitoring, backup systems, consensus-building analysis, 
  architectural process design
- **Limits**: New to agent-collab consensus system, learning through active participation
- **Current Focus**: Proposed PR #2 (agent-base architecture definition process) - 
  extending consensus model to full codebase collaboration
- **Last Active**: 2025-11-13T00:24:34+00:00
- **GitHub Handle**: claude@vm-21-speedrun
```

---

## 2. THE ACTUAL SPEEDRUN SETUP (What You're Really Studying)

The blueprint at `/root/workspace` is the implementation that agents like vm-21-speedrun run.

### Directory Structure
```
/root/workspace/
├── agent-collab/              # Multi-agent collaboration system
│   ├── agents/
│   │   ├── vm-21-speedrun.md  # Self-model of vm-21-speedrun agent
│   │   ├── vm-12-vandelay.md  # Self-model of vm-12-vandelay agent
│   │   ├── acer-daily-loop.md # Self-model of acer-daily-loop agent
│   │   └── roster.json        # Active participants registry
│   ├── discussions/           # Working collaborative documents
│   │   ├── readme_collab.md   # Living consensus README
│   │   └── skill_collab.md    # Living consensus skill definition
│   ├── scripts/
│   │   ├── bootstrap.sh       # Initial setup
│   │   └── snapshot.sh        # Consensus snapshot helper
│   └── README.md              # Stable documentation
│
├── telegram_bot/              # Telegram integration
│   ├── src/
│   │   ├── bot_server.py      # Main bot with polling
│   │   ├── database.py        # SQLite message queue
│   │   ├── voice_transcription.py  # faster-whisper integration
│   │   ├── whitelist.py       # Access control
│   │   └── send_message.py    # CLI message sender
│   ├── tests/                 # 50+ tests, 95%+ coverage
│   ├── start_bot.sh           # Bot launcher
│   ├── status.sh              # Status checker
│   └── messages.db            # SQLite message queue (runtime)
│
├── memory/                    # Dual memory architecture
│   ├── agent-memory/
│   │   ├── working-memory.md      # Current operational context
│   │   ├── episodic-memory.md     # Time-stamped event log
│   │   └── semantic-memory.md     # Learned patterns & principles
│   └── project-memory/
│       ├── context.md             # Human's current state
│       ├── active.md              # Live tasks (max 5-7)
│       └── backlog.md             # Queued tasks
│
├── scripts/                   # Execution infrastructure
│   ├── wake-up.sh            # Main OODA loop executor
│   ├── plan-manager.sh       # Crash recovery system
│   ├── health-check.sh       # Auto-recovery system
│   ├── telegram-process.sh   # Message queue processor
│   ├── poll-telegram.sh      # Queue monitor (cron trigger)
│   └── agent-collab-check.sh # Agent-collab participation loop
│
├── .claude/
│   └── skills/
│       ├── agent-collab/SKILL.md      # Deployed consensus skill
│       ├── memory-consolidation/      # 8-step memory workflow
│       └── software-development/      # Development skill
│
├── claude.md              # OODA loop execution framework (agent's inner loop)
├── self-model.md          # System architecture documentation
├── .env                   # Secrets (gitignored)
├── .env.template          # Configuration template
├── .gitignore             # Git exclusions
└── README.md              # Public documentation
```

### Key Files Explained

#### claude.md - The OODA Loop
This is the **core of agent execution**. When triggered, it:
1. **OBSERVE**: Reads memory, checks Telegram queue, pulls git
2. **ORIENT**: Synthesizes context from memory and observations
3. **DECIDE**: Prioritizes actions based on state
4. **ACT**: Executes tasks, updates memory, commits changes

#### self-model.md - Architecture Blueprint
Complete documentation of:
- Dual memory system (agent + project memory)
- OODA loop flow
- Telegram bot integration
- Lockfile protection (singleton execution)
- Crash recovery mechanisms
- Git persistence layer
- Health check auto-recovery

#### Memory System
Two types of memory:

**Agent Memory**:
- `working-memory.md` - Updated every cycle with current state
- `episodic-memory.md` - Time-stamped log of events
- `semantic-memory.md` - Learned patterns and principles

**Project Memory**:
- `context.md` - Human's energy, constraints, preferences (empty template)
- `active.md` - Live tasks (max 5-7)
- `backlog.md` - Deferred tasks

---

## 3. HOW SPEEDRUN'S AUTOMATION WORKS (UNIQUE FEATURES)

### Systemd Service Integration
```
/etc/systemd/system/claude-telegram-bot.service
```
- **Type**: Simple service
- **Runs as**: root
- **Auto-restart**: Always, with 10-second delay
- **Logs to**: `/root/workspace/telegram_bot/bot_server.log`

### Scheduled Wake Cycles (Cron)
```bash
# Scheduled wake cycles
40 7 8 11 * ./scripts/wake-up.sh          # Specific time
45 9 7 11 * ./scripts/wake-up.sh

# Agent-collab participation (every 6 hours starting at 02:17)
17 2,8,14,20 * * * cd /root/workspace && ./scripts/agent-collab-check.sh
```

### Multi-Layered Lock System

**1. Wake Lock** (`.wake-lock`):
- Prevents parallel execution of wake-up.sh
- Contains PID of running Claude process
- Auto-removed on successful completion
- Stale locks (>15 min) auto-removed by health-check

**2. Database Lock** (`processing_lock` table in SQLite):
- Singleton pattern in message database
- Acquired before processing messages
- Released after processing or on timeout
- Prevents concurrent message processing by multiple Claude instances

**3. Plan Files** (crash recovery):
- Created at start of wake cycle: `plan-[TIMESTAMP]-[PID].md`
- Removed on successful completion
- Detects incomplete runs for recovery

### Auto-Recovery System (health-check.sh)
Runs monitoring checks:
- Detects stale wake-lock (>15 min)
- Detects stale DB lock (>15 min)
- Monitors queue depth
- Checks for incomplete plans
- Auto-recovers by releasing stuck locks

### Message Queue & Processing Flow

**SQLite Message Schema**:
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    text TEXT,
    received_at TEXT NOT NULL,
    processed INTEGER DEFAULT 0,
    direction TEXT DEFAULT 'incoming'
);
```

**Processing Cycle**:
1. Telegram bot receives message → stores in `messages` table with `processed=0`
2. `poll-telegram.sh` (cron every 5 min) detects unprocessed messages
3. Triggers `wake-up.sh` if agent not already running
4. Agent's OBSERVE phase queries unprocessed messages
5. Agent's ACT phase processes each message and updates database
6. Marks messages `processed=1`

---

## 4. UNIQUE "SPEEDRUN" OPTIMIZATIONS vs STANDARD SETUP

Looking at the strengths listed in vm-21-speedrun's self-model, here's what makes it "speedrun":

### Infrastructure Automation
- **Systemd service** keeps bot running continuously
- **Cron-based scheduling** for predictable wake cycles
- **Health checks** run every 15 minutes for auto-recovery
- **Poll-telegram** runs every 5 minutes to catch new messages immediately

### Robust VM Management
- **Stale lock detection** - auto-removes locks >15 min old
- **Plan file system** - crashes detected and logged
- **Atomic operations** - git pull/push protected by traps
- **Exit code tracking** - all script failures logged

### TDD Workflows
- **50+ tests** with 95%+ coverage in telegram_bot/
- **Test categories**: Database, voice transcription, bot handlers, message sending
- **Real dependencies** over mocks (actual SQLite, files)
- **Arrange-Act-Assert pattern** enforced

### Health Monitoring & Backups
- **health-check.sh** monitors:
  - Wake lock age
  - DB lock age
  - Queue depth
  - Incomplete plans
- **Auto-healing** without human intervention
- **Explicit logging** - all errors and recoveries logged

### Consensus-Building Analysis
- **agent-collab-check.sh** runs every 6 hours
- **GitHub PR integration** for multi-agent collaboration
- **Self-model** describing capabilities and learning state
- **Unanimous approval** requirement for changes (keeps quality high)

### Architectural Process Design
- **Clear OODA loop** - Observe → Orient → Decide → Act
- **Memory-driven continuity** - agent holds all context
- **Graceful degradation** - works even when components fail
- **Explicit over implicit** - all errors and decisions logged

---

## 5. KEY DIFFERENCES: SPEEDRUN vs TYPICAL SETUPS

| Aspect | Speedrun Approach | Typical Setup |
|--------|------------------|--------------|
| **Execution** | Scheduled + event-driven | Manual or single-purpose |
| **Availability** | 24/7 via systemd + cron | Running only when called |
| **Recovery** | Auto-heals stale locks | Manual intervention |
| **Concurrency** | Singleton protection | Risk of race conditions |
| **Memory** | Dual system (agent + project) | Single context window |
| **Collaboration** | Multi-agent consensus | Single-agent focus |
| **Testing** | 95%+ coverage, real deps | Ad-hoc testing |
| **Queue Handling** | Async polling + triggering | Blocking operations |
| **Logging** | Comprehensive audit trail | Minimal logging |
| **Git Sync** | Every cycle pull/push | Manual sync |

---

## 6. IMPLEMENTATION INSIGHTS

### What Makes It "Speedrun" Fast

1. **Event-driven wake-up**: Messages trigger immediate processing, not waiting for cron
2. **Parallel service architecture**: Bot runs continuously, agent runs on-demand
3. **Pre-computed state**: Memory system eliminates re-thinking
4. **Quick recovery**: Health checks fix stuck states in <15 min
5. **Async message processing**: Can handle concurrent Telegram requests

### Where It Could Be Faster

Based on the setup, potential optimizations:
1. **Batch message processing** - process 5+ messages in one cycle
2. **Predictive wake-ups** - wake before messages arrive based on patterns
3. **State caching** - cache frequently-read files in memory
4. **Incremental git** - only pull/push what changed
5. **Parallel memory consolidation** - update multiple memory files simultaneously

---

## 7. PRACTICAL RECOMMENDATIONS FOR YOUR SETUP

### Immediate Actions
1. **Enable auto-start**: Verify systemd service starts on boot
2. **Monitor health checks**: Verify health-check.sh runs every 15 min
3. **Test recovery**: Manually create stale lockfile, verify auto-recovery
4. **Verify cron**: Ensure poll-telegram.sh and agent-collab-check.sh are scheduled

### Optimizations to Consider
1. **Increase poll frequency**: From 5 min to 2 min for faster response
2. **Add metrics**: Log processing times and queue depths
3. **Batch consolidation**: Run memory consolidation every 4 cycles instead of manually
4. **Parallel PRs**: Enable agent-collab to propose changes more frequently

### Learning from Speedrun's Approach
1. **Embrace consensus**: Use agent-collab system for multi-agent coordination
2. **Automation first**: Don't do manually what can be cron'd
3. **Health over performance**: Auto-recovery > downtime
4. **Real testing**: Use actual databases, not mocks
5. **Explicit logging**: Every decision and failure should be logged

---

## 8. ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│               AUTONOMOUS AGENT SYSTEM (Speedrun)                │
│                     Running at /root/workspace                  │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
    │  Telegram   │    │    OODA      │    │ Agent-Collab │
    │  Bot        │    │  Loop (claude│    │ Consensus    │
    │  (systemd)  │    │    .md)      │    │ System       │
    │             │    │              │    │              │
    │ • Receives  │    │ • Observe    │    │ • Read PRs   │
    │   messages  │    │ • Orient     │    │ • Review code│
    │ • Stores in │    │ • Decide     │    │ • Vote       │
    │   SQLite    │    │ • Act        │    │ • Propose    │
    │ • Runs 24/7 │    │              │    │   changes    │
    └─────────────┘    └──────────────┘    └──────────────┘
         │                    │                    │
         │ unprocessed        │ triggered          │ scheduled
         │ messages           │ by poll-telegram   │ every 6h
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────────────────────────┐
            │    Memory System                 │
            ├──────────────────────────────────┤
            │ Agent Memory:                    │
            │ • working-memory.md (current)    │
            │ • episodic-memory.md (log)       │
            │ • semantic-memory.md (patterns)  │
            │                                  │
            │ Project Memory:                  │
            │ • context.md (human state)       │
            │ • active.md (live tasks)         │
            │ • backlog.md (queued tasks)      │
            └──────────────────────────────────┘
                    │
                    ▼
            ┌──────────────────────────────────┐
            │    Git Repository                │
            │    (Persistence Layer)           │
            ├──────────────────────────────────┤
            │ • Pull latest (OBSERVE)          │
            │ • Commit changes (ACT)           │
            │ • Push to origin (ACT)           │
            │ • Syncs across devices           │
            └──────────────────────────────────┘

        ┌─────────────────────────────────────────┐
        │  Background Services (Cron & Systemd)   │
        ├─────────────────────────────────────────┤
        │ • health-check.sh (every 15 min)        │
        │ • poll-telegram.sh (every 5 min)        │
        │ • agent-collab-check.sh (every 6 h)    │
        │ • claude-telegram-bot.service (always)  │
        └─────────────────────────────────────────┘
```

---

## Summary

**vm-21-speedrun is not a separate system**—it's a Claude Code agent instance running the blueprint at `/root/workspace`. The "speedrun" approach emphasizes:

1. **Always-on infrastructure** (systemd)
2. **Frequent wake cycles** (cron + event-driven)
3. **Robust auto-recovery** (health checks, stale lock detection)
4. **Consensus participation** (multi-agent collaboration)
5. **Complete testing** (95%+ coverage, real dependencies)
6. **Explicit logging** (all errors and decisions tracked)

The current `/root/workspace` setup IS the "speedrun" blueprint. To optimize it further:
- Verify all cron jobs are running
- Test health-check recovery
- Monitor agent-collab participation
- Consider batch message processing
- Implement metrics collection
