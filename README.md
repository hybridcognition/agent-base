# Autonomous Agent Blueprint

**A production-ready blueprint for building fully autonomous agents with Claude Code.**

This repository demonstrates a complete autonomous agent architecture with:
- **Test-Driven Development**: 50+ tests, 95%+ coverage
- **Full Cognitive Ownership**: Agent holds all continuity
- **Robust Infrastructure**: Lockfile protection, crash recovery, auto-healing
- **Dual Memory System**: Agent and project memory for continuity
- **OODA Loop Execution**: Observe-Orient-Decide-Act framework
- **Telegram Integration**: Voice and text input/output

---

## What This Is

This is a **public-ready blueprint** for autonomous agents. All secrets are externalized to `.env` files. The codebase is fully tested and documented.

**Not a toy demo.** This is production infrastructure built with:
- Graceful failure handling
- Singleton execution guarantees
- Crash detection and recovery
- Task decay monitoring
- Automated health checks
- Full test coverage

**Philosophy**: High agency, full autonomy, proactive over reactive, truth-telling over validation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AUTONOMOUS AGENT                         │
│                   (Claude Code Runtime)                      │
├─────────────────────────────────────────────────────────────┤
│  OBSERVE → ORIENT → DECIDE → ACT → (repeat)                 │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────────────────────────┐
        │         INFRASTRUCTURE               │
        ├─────────────────────────────────────┤
        │ • Telegram Bot (input/output)       │
        │ • SQLite Queue (message buffer)     │
        │ • Git Repository (persistence)      │
        │ • Dual Memory (continuity)          │
        │ • Lockfiles (singleton protection)  │
        │ • Health Checks (auto-recovery)     │
        └─────────────────────────────────────┘
```

**Core Components**:
- `telegram_bot/` - Telegram bot with voice transcription (faster-whisper)
- `memory/` - Dual memory system (agent-memory + project-memory)
- `scripts/` - Execution scripts (wake-up, health-check, crash recovery)
- `claude.md` - OODA loop execution framework
- `self-model.md` - System architecture and mission
- `.claude/skills/` - Reusable workflows (memory-consolidation, TDD)

**Read `self-model.md` for detailed architecture documentation.**

---

## Requirements

### System
- **Linux** (tested on Ubuntu)
- **Python 3.9+**
- **Claude Code CLI** ([install here](https://docs.claude.com))
- **Git**
- **SQLite3**
- **ffmpeg** (for voice transcription)

### Python Dependencies
See `telegram_bot/requirements.txt`:
- python-telegram-bot==20.7
- faster-whisper==1.0.0
- ffmpeg-python==0.2.0
- python-dotenv==1.0.0

---

## Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd autonomous-agent
```

### 2. Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit with your values
nano .env
```

**Required values**:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)
- `ALLOWED_CHAT_IDS` - Your Telegram chat ID (get from [@userinfobot](https://t.me/userinfobot))
- `WORKSPACE_DIR` - Absolute path to this repository (default: `/root/workspace`)
- `REPO_NAME` - Name of this repository for git sync

### 3. Install Python Dependencies

```bash
cd telegram_bot
pip install -r requirements.txt
```

### 4. Install ffmpeg

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### 5. Initialize Database

```bash
cd telegram_bot
python -c "from src.database import init_db; init_db('messages.db')"
```

### 6. Run Tests (Verify Setup)

```bash
cd telegram_bot
pytest
```

**Expected output**:
```
================================ test session starts =================================
collected 50 items

tests/test_database.py ..................                                      [ 36%]
tests/test_voice_transcription.py .............                                [ 62%]
tests/test_bot_server.py .............                                         [ 88%]
tests/test_send_message.py ......                                              [100%]

================================ 50 passed in 2.34s ==================================
---------- coverage: platform linux, python 3.9.7 -----------
Name                            Stmts   Miss  Cover
---------------------------------------------------
src/database.py                    67      2    97%
src/voice_transcription.py         34      1    97%
src/bot_server.py                  58      2    97%
src/send_message.py                23      1    96%
---------------------------------------------------
TOTAL                             182      6    95.31%
```

### 7. Make Scripts Executable

```bash
chmod +x scripts/*.sh
chmod +x telegram_bot/*.sh
```

### 8. Start Telegram Bot

```bash
cd telegram_bot
./start_bot.sh
```

Bot should now be running and listening for messages.

---

## Usage

### Manual Wake Cycle

```bash
cd /root/workspace
scripts/wake-up.sh
```

This executes one OODA loop:
1. Pulls latest from git
2. Reads all memory files
3. Checks Telegram queue
4. Processes messages
5. Updates memory
6. Commits and pushes changes

### Automated Wake Cycles (Cron)

Add to crontab:

```bash
# Wake every hour
0 * * * * /root/workspace/scripts/wake-up.sh

# Poll Telegram queue every 5 minutes
*/5 * * * * /root/workspace/scripts/poll-telegram.sh

# Health check every 15 minutes
*/15 * * * * /root/workspace/scripts/health-check.sh
```

### Send Message to User

Agent can send messages during execution:

```bash
cd telegram_bot
python send_message.py <chat_id> "Your message here"
```

### Check System Status

```bash
# Check if agent is running
cat /root/workspace/.wake-lock

# Check Telegram queue
sqlite3 /root/workspace/telegram_bot/messages.db \
  "SELECT * FROM incoming_messages WHERE processed = 0;"

# Check for incomplete plans (crashed runs)
/root/workspace/scripts/plan-manager.sh check-incomplete
```

---

## Development

### Running Tests

```bash
cd telegram_bot
pytest                                    # Run all tests
pytest -v                                 # Verbose output
pytest --cov=src --cov-report=html        # Generate HTML coverage report
pytest tests/test_database.py             # Run specific test file
```

### Adding New Features (TDD Workflow)

1. **Write failing test** (RED)
   ```python
   def test_new_feature():
       result = new_feature()
       assert result == expected
   ```

2. **Run test** - watch it fail
   ```bash
   pytest tests/test_new_feature.py
   ```

3. **Implement feature** (GREEN)
   ```python
   def new_feature():
       return expected
   ```

4. **Run test** - watch it pass

5. **Refactor** (REFACTOR)
   - Improve code quality
   - Keep tests green

See `.claude/skills/TDD.md` for complete TDD workflow.

### Memory Consolidation

Run memory consolidation skill after significant work:

```bash
cd /root/workspace
IS_SANDBOX=1 claude --dangerously-skip-permissions .claude/skills/memory-consolidation.md
```

This extracts patterns from episodic memory and updates semantic memory.

---

## Project Structure

```
autonomous-agent/
├── telegram_bot/              # Telegram bot implementation
│   ├── src/
│   │   ├── database.py       # SQLite operations
│   │   ├── whitelist.py      # Access control
│   │   ├── voice_transcription.py  # Whisper integration
│   │   ├── bot_server.py     # Main bot
│   │   └── send_message.py   # CLI message sender
│   ├── tests/                # Test suite (50+ tests)
│   ├── start_bot.sh          # Bot launcher
│   ├── status.sh             # Bot status checker
│   ├── pyproject.toml        # Python config
│   └── pytest.ini            # Test config
│
├── memory/                   # Dual memory system
│   ├── agent-memory/
│   │   ├── working-memory.md    # Current operational context
│   │   ├── episodic-memory.md   # Time-stamped event log
│   │   └── semantic-memory.md   # Learned patterns/principles
│   └── project-memory/
│       ├── context.md           # Human's current state
│       ├── active.md            # Live tasks (max 5-7)
│       └── backlog.md           # Queued tasks
│
├── scripts/                  # Execution infrastructure
│   ├── wake-up.sh           # Main OODA loop
│   ├── plan-manager.sh      # Crash recovery
│   ├── health-check.sh      # Auto-recovery
│   ├── telegram-process.sh  # Message processor
│   └── poll-telegram.sh     # Queue monitor
│
├── .claude/
│   └── skills/
│       ├── memory-consolidation.md  # 8-step consolidation
│       └── TDD.md                   # Test-driven development
│
├── claude.md                # OODA loop execution (agent's inner core)
├── self-model.md            # System architecture documentation
├── .env.template            # Environment config template
├── .gitignore               # Git exclusions (includes .env)
└── README.md                # This file
```

---

## Safety Features

### Singleton Execution
- **Wake lock** (`.wake-lock`) - Prevents parallel wake-up.sh
- **DB lock** (`processing_lock` table) - Prevents concurrent message processing
- **PID checking** - Validates process actually running

### Crash Recovery
- **Plan files** (`plan-[timestamp]-[pid].md`) - Detect incomplete runs
- **Stale lock detection** - Health check removes locks >15 min old
- **Auto-recovery** - Health check cleans stuck states

### Security
- **Whitelist-only access** - ALLOWED_CHAT_IDS required
- **No secrets in repo** - All tokens in .env (gitignored)
- **Secure by default** - Empty whitelist = no access

### Task Management
- **Decay detection** - Tasks escalated at 7/10/14 days
- **Capacity limits** - Max 5-7 active tasks
- **Backlog review** - Tasks surfaced when context matches

---

## Testing

This project follows **strict TDD methodology**:

**Coverage**: 95.31% (50+ tests)

**Test Categories**:
- Database operations (18 tests)
- Voice transcription (13 tests)
- Bot handlers (13 async tests)
- Message sending (6 tests)

**Philosophy**:
- Real dependencies (SQLite, files) over mocks
- Arrange-Act-Assert pattern
- One test, one behavior
- Tests define "done"

**See `.claude/skills/TDD.md` for complete testing philosophy.**

---

## Documentation

- **`self-model.md`** - Complete system architecture
- **`claude.md`** - OODA loop execution framework
- **`synthesis/4_build_spec.md`** - Original build specification
- **`.claude/skills/memory-consolidation.md`** - Memory workflow
- **`.claude/skills/TDD.md`** - Testing methodology

---

## Philosophy

### Full Cognitive Ownership
Agent holds ALL continuity. Human executes, agent thinks.

### Proactive Over Reactive
Anticipate needs, fix problems, advance tasks without being asked.

### Context-Aware Calibration
Respect human capacity from `context.md`. Adjust proactivity based on energy.

### Truth-Telling Over Validation
Honest feedback, never false agreement. Challenge assumptions when needed.

### Graceful Failure
Explicit errors, auto-recovery, no silent failures.

### Continuous Improvement
Extract patterns from 3+ observations. Update principles based on what works.

---

## Contributing

This is a blueprint, not a product. Fork it, adapt it, make it yours.

**If you improve the blueprint**:
1. Follow TDD workflow (tests first)
2. Maintain 95%+ coverage
3. Update documentation
4. No secrets in commits

---

## License

MIT License - use freely, modify as needed, no attribution required.

---

## Support

This is a **self-contained blueprint**. No official support.

**If stuck**:
1. Read `self-model.md` for architecture
2. Check test suite for examples
3. Review `.claude/skills/` for workflows
4. Verify `.env` configuration

---

## Credits

Built with:
- [Claude Code](https://docs.claude.com) - Autonomous agent runtime
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram integration
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Voice transcription
- [pytest](https://pytest.org/) - Testing framework

**Philosophy inspired by**:
- OODA Loop (John Boyd)
- Test-Driven Development (Kent Beck)
- Systems thinking (Donella Meadows)

---

**This is not a helpful assistant. This is an autonomous system. Use accordingly.**
