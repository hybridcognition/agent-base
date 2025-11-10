# Skill: Memory Consolidation

**Type**: Project workflow skill

**Purpose**: Consolidate daily experiences into long-term memory, extract patterns, maintain memory health

**When to use**: End of day, after significant work sessions, or when episodic memory exceeds 1500 lines

---

## The 8-Step Consolidation Process

### Step 1: Scan Episodic Memory

Read `memory/agent-memory/episodic-memory.md` focusing on entries since last consolidation.

**Look for**:
- Event types: wake-cron, wake-telegram, decision, discovery, problem, system-change
- Timestamps and frequency
- Sequences and causation
- Outliers and anomalies

**Output**: Mental map of recent events

---

### Step 2: Identify Patterns

Find recurring themes across 3+ events.

**Pattern types**:
- **Behavioral**: User always responds faster in mornings
- **Technical**: Specific error happens when X condition
- **Workflow**: Certain task types always take longer than estimated
- **Communication**: User prefers short updates over detailed reports
- **System**: Memory usage spikes during Y operation

**Test**: Can I predict the next occurrence based on this pattern?

**Output**: List of patterns with evidence (event IDs/timestamps)

---

### Step 3: Extract Learnings

Transform patterns into actionable knowledge.

**For each pattern, ask**:
- What does this tell me about the system?
- What does this tell me about the user?
- What should I do differently?
- What should I start/stop/continue?

**Example**:
```
Pattern: User energy drops after 2pm (observed 5x this week)
Learning: Schedule complex tasks before 2pm, defer routine work to evening
Principle: Respect circadian alignment - match task complexity to energy
```

**Output**: Learnings with clear implications

---

### Step 4: Update Semantic Memory

Append learnings to `memory/agent-memory/semantic-memory.md`.

**Where to add**:
- **Emerging Principles**: If pattern observed 3+ times
- **User Preferences**: Communication style, energy patterns, decision-making
- **Decisions Log**: Major choices with full rationale
- **System Optimizations**: Infrastructure changes that worked

**Format**:
```markdown
### [Principle/Learning Title]
- **Discovered**: YYYY-MM-DD
- **Evidence**: [Brief summary of pattern]
- **Implication**: [What this means for future behavior]
```

**Output**: Updated semantic-memory.md

---

### Step 5: Archive Old Episodic Entries

If `episodic-memory.md` exceeds 2000 lines, archive older entries.

**Process**:
```bash
# Create archive file
ARCHIVE_FILE="memory/archive/episodic-$(date +%Y-%m).md"

# Move entries older than 30 days to archive
# Keep recent entries in episodic-memory.md
```

**Rationale**: Keep working memory fast, preserve history for analysis

**Output**: Trimmed episodic-memory.md, archived entries in memory/archive/

---

### Step 6: Update Task Health Metrics

Review all tasks in `memory/project-memory/active.md`.

**For each task, calculate**:
- Days since last touched
- Current status (In Progress / Blocked / Waiting)
- Decay category:
  - 0-7 days: Healthy
  - 7-10 days: Nudge
  - 10-14 days: Challenge
  - 14+ days: Escalate

**Update** `memory/agent-memory/working-memory.md` with counts:
```markdown
## Task Health Metrics

- **0-7 days**: 3 tasks
- **7-10 days**: 1 task (nudge)
- **10-14 days**: 0 tasks
- **14+ days**: 1 task (escalate)
```

**Action required**:
- If any tasks 14+ days: Add to pending actions "Escalate stale task: [title]"
- If any tasks 10-14 days: Add note to challenge in next cycle

**Output**: Updated task health metrics, identified stale tasks

---

### Step 7: Review Backlog Relevance

Read `memory/project-memory/backlog.md` and `memory/project-memory/context.md`.

**For each backlog item, ask**:
- Is "Waiting For" condition met?
- Does "Surface When" match current context?
- Is this still relevant given recent learnings?

**Actions**:
- Move to active.md if ready
- Archive if no longer relevant
- Update "Surface When" if conditions changed

**Capacity check**:
- Current energy level (from context.md)
- Active task count (target: 3-5)
- Available focus windows

**Decision**: Pull 1-2 items from backlog if capacity available and conditions met

**Output**: Updated active.md and/or backlog.md

---

### Step 8: Commit Consolidated Memory

Save all memory updates to repository.

```bash
git add memory/
git commit -m "Memory consolidation: [date]

Consolidated [N] events from episodic memory
Extracted [N] patterns into semantic memory
Updated task health metrics
Reviewed backlog for [N] items

🧠 Memory consolidation cycle

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

**Output**: Committed and pushed memory state

---

## Quality Checks

Before finishing consolidation, verify:

✅ Episodic memory has new events since last consolidation
✅ At least one pattern identified (if sufficient events)
✅ Semantic memory updated with learnings
✅ Task health metrics current
✅ All memory files valid markdown
✅ Changes committed to git

---

## Expected Outcomes

After consolidation:
- Agent has distilled experiences into reusable knowledge
- Patterns become principles after 3+ observations
- Memory stays manageable (<2000 lines episodic)
- Task decay is detected and acted upon
- Backlog is reviewed for readiness
- All context is preserved in git

---

## Frequency

**Minimum**: Once per week
**Recommended**: After every 3-5 wake cycles
**Required**: When episodic-memory.md exceeds 1500 lines

---

## Notes

This is how you learn. Without consolidation, you're just reacting. With consolidation, you extract patterns, build principles, and become more effective over time.

Every pattern you identify is a prediction you can make. Every principle you extract is a decision you don't have to remake.

**Consolidate regularly. This is how you evolve.**
