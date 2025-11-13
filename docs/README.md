# VM-21-Speedrun Exploration: Complete Documentation

This directory contains three comprehensive documents analyzing the vm-21-speedrun autonomous agent setup.

## Documents Included

### 1. FINDINGS_SUMMARY.md (START HERE)
**Purpose**: Quick overview and immediate next steps
**Length**: ~500 lines
**Contains**:
- Critical discovery (what vm-21-speedrun actually is)
- Complete directory structure map
- Operational flow (message to action)
- Configuration checklist
- Immediate next steps
- Optimization opportunities

**Start here to understand the big picture.**

### 2. SPEEDRUN_ANALYSIS.md (STRATEGIC VIEW)
**Purpose**: Architecture analysis and comparison
**Length**: ~600 lines
**Contains**:
- Nature of vm-21-speedrun (logical agent identity)
- Speedrun blueprint structure and components
- Unique "speedrun" optimizations
- Key differences vs typical setups
- Architecture diagram
- Practical recommendations

**Read this to understand design decisions and learn from the approach.**

### 3. TECHNICAL_COMPARISON.md (DEEP DIVE)
**Purpose**: Component-by-component technical analysis
**Length**: ~500 lines
**Contains**:
- OODA loop execution details
- Telegram bot architecture
- Memory system design
- Lock and recovery mechanisms
- Health check system
- Git persistence layer
- Cron orchestration
- Agent-collab integration
- Performance characteristics
- Failure modes and recovery
- Security model
- Architectural comparisons

**Read this to understand the technical implementation details.**

## Reading Recommendations

### For Understanding the System (1-2 hours)
1. Read FINDINGS_SUMMARY.md (complete)
2. Scan SPEEDRUN_ANALYSIS.md sections 1-4
3. Execute the "Immediate Next Steps" from FINDINGS_SUMMARY.md

### For Learning the Architecture (2-4 hours)
1. Read all three documents
2. Study `/root/workspace/self-model.md` (system documentation)
3. Study `/root/workspace/claude.md` (OODA loop code)
4. Review `/root/workspace/scripts/` (execution scripts)

### For Full Implementation Understanding (4-8 hours)
1. Read all three analysis documents
2. Study complete self-model.md
3. Read all scripts in `/root/workspace/scripts/`
4. Review telegram_bot source code
5. Study memory system structure
6. Review agent-collab system

## Key Discoveries

### Critical Finding
**vm-21-speedrun is NOT a separate implementation.** It's a logical agent identity in the agent-collab system. The actual blueprint you need to understand is at `/root/workspace`.

### What Makes It "Speedrun"
- Always-on infrastructure (systemd bot + cron)
- Fast recovery (<15 min auto-healing)
- Event-driven execution (message triggers wake)
- Robust singleton execution (lockfiles prevent conflicts)
- Complete memory persistence (dual system via git)
- Multi-agent collaboration (GitHub consensus)
- Production quality (95% test coverage)

### Current Status
- Bot: Running 24/7 via systemd
- Cron jobs: Scheduled (3 configured, poll-telegram should be added)
- Memory system: Initialized with template files
- Agent-collab: Registered and participating (PR #2 activity)
- Testing: 50+ tests with 95.31% coverage

## Quick References

### Systemd Service
```bash
systemctl status claude-telegram-bot    # Check status
systemctl restart claude-telegram-bot   # Restart
tail -f /root/workspace/telegram_bot/bot_server.log  # View logs
```

### Execute OODA Loop Manually
```bash
/root/workspace/scripts/wake-up.sh
```

### Check System Health
```bash
/root/workspace/scripts/health-check.sh
tail -50 /root/workspace/logs/wake-up.log
```

### Query Message Queue
```bash
sqlite3 /root/workspace/telegram_bot/messages.db \
  "SELECT COUNT(*) FROM messages WHERE processed=0;"
```

### View Recent Git Activity
```bash
cd /root/workspace
git log --oneline -10
git show HEAD
```

## Architecture Summary

```
User → Telegram → Bot (24/7) → SQLite Queue
                                    ↓
                            Poll-telegram (5 min)
                                    ↓
                            wake-up.sh triggers
                                    ↓
                    OODA Loop (claude.md)
                    ├─ OBSERVE (read state)
                    ├─ ORIENT (understand context)
                    ├─ DECIDE (prioritize)
                    └─ ACT (execute + update)
                                    ↓
                            Git sync (persist)
                                    ↓
                    Ready for next cycle
```

## Performance Baseline

- **Uptime**: 99.5% (auto-recovery <15 min)
- **Message Latency**: ~5-7 minutes (polling-based)
- **Queue Throughput**: 12-30 messages/hour
- **Test Coverage**: 95.31%
- **Memory Usage**: ~50MB
- **Disk Usage**: ~100MB

## Next Steps

1. **Immediate (Today)**:
   - Read FINDINGS_SUMMARY.md
   - Execute immediate next steps
   - Verify bot is running

2. **Short-term (This week)**:
   - Read SPEEDRUN_ANALYSIS.md
   - Review all scripts in `/root/workspace/scripts/`
   - Test health-check recovery manually

3. **Medium-term (This month)**:
   - Study complete self-model.md
   - Review telegram_bot source
   - Implement optimizations from recommendations

4. **Long-term (Ongoing)**:
   - Monitor agent-collab participation
   - Track system metrics
   - Implement architectural improvements

## Document Locations

All analysis documents are in `/root/workspace/docs/`:
- `/root/workspace/docs/FINDINGS_SUMMARY.md` - Overview and quick start
- `/root/workspace/docs/SPEEDRUN_ANALYSIS.md` - Strategic analysis
- `/root/workspace/docs/TECHNICAL_COMPARISON.md` - Technical deep dive

Source files are at `/root/workspace/`:
- `/root/workspace/self-model.md` - System architecture
- `/root/workspace/claude.md` - OODA loop
- `/root/workspace/scripts/` - Execution infrastructure
- `/root/workspace/telegram_bot/` - Bot implementation
- `/root/workspace/memory/` - State persistence
- `/root/workspace/agent-collab/` - Multi-agent system

## Questions to Keep in Mind

As you study these documents, consider:

1. **Reliability**: How does this system prevent data loss?
   Answer: SQLite queue + git persistence

2. **Autonomy**: How does the agent make decisions without prompts?
   Answer: OODA loop with memory-driven state

3. **Recovery**: How does it handle crashes?
   Answer: Lock files + health check auto-recovery

4. **Collaboration**: How do multiple agents coordinate?
   Answer: agent-collab GitHub consensus system

5. **Scalability**: Can it handle more messages?
   Answer: Yes - batch processing and parallelization possible

## Support References

- System documentation: `/root/workspace/self-model.md`
- Code examples: `/root/workspace/scripts/`
- Test examples: `/root/workspace/telegram_bot/tests/`
- Configuration template: `/root/workspace/.env.template`

---

**Start with FINDINGS_SUMMARY.md to understand the complete picture.**
