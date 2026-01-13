# Skill: Memory Consolidation

**Type**: Project workflow skill

**Purpose**: Consolidate daily experiences into long-term memory, extract patterns, maintain memory health

**When to use**: End of day, after significant work sessions, or when episodic memory exceeds 1500 lines

---

## The 8-Step Consolidation Process

### Step 1: Scan Episodic Memory

Read `memory/episodic-memory.md` focusing on entries since last consolidation.

**Look for**:
- Event types: wake-cron, wake-trigger, decision, discovery, problem, system-change
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

Append learnings to `memory/semantic-memory.md`.

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

If `memory/episodic-memory.md` exceeds 2000 lines, archive older entries.

**Process**:
```bash
# Create archive file
ARCHIVE_FILE="memory/archive/episodic-$(date +%Y-%m-%d).md"

# Move entries older than 30 days to archive
# Keep recent entries in episodic-memory.md
# Add note at top: "Previous archive: [filename] (N lines)"
```

**Rationale**: Keep working memory fast, preserve history for analysis

**Output**: Trimmed episodic-memory.md, archived entries in memory/archive/

---

### Step 6: Update Working Memory Status

Review `memory/working-memory.md` and update:

**Task Health Metrics** (if tracking tasks):
- 0-7 days: Healthy
- 7-10 days: Nudge
- 10-14 days: Challenge
- 14+ days: Escalate

**Current Status**: Update "Right Now" section with accurate present state

**Pending Actions**: Remove completed items, add new blockers

**Output**: Updated working-memory.md with current state

---

### Step 7: Update Active Hypotheses

Review the Active Hypotheses table in `memory/working-memory.md`.

**For each hypothesis**:
- Do recent events provide evidence for/against?
- Can status be updated (Active → Confirmed/Rejected)?
- Should new hypotheses be added?

**Format**:
```markdown
| Question | Hypothesis | Test Criteria | Status |
|----------|-----------|---------------|--------|
| Why X? | Because Y | Observe Z 3x | Confirmed |
```

**Output**: Updated hypotheses with status changes

---

### Step 8: Commit Consolidated Memory

Save all memory updates to repository.

```bash
git add memory/
git commit -m "Memory consolidation: [date]

Consolidated [N] events from episodic memory
Extracted [N] patterns into semantic memory
Updated working memory status
Reviewed hypotheses

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
✅ Working memory reflects current state
✅ All memory files valid markdown
✅ Changes committed to git

---

## Expected Outcomes

After consolidation:
- Agent has distilled experiences into reusable knowledge
- Patterns become principles after 3+ observations
- Memory stays manageable (<2000 lines episodic)
- Working memory reflects current reality
- Hypotheses are tracked and updated
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
