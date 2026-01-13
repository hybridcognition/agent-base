# Episodic Memory

Time-stamped information, append only as a hard rule.

---

## Usage Instructions

**Purpose:** Your time-stamped event log. This is the source of truth for "what happened when."

**What belongs here:**
- Wake history: One line per wake-up (date/time | type | summary)
- All significant events with timestamps
- User interactions and responses
- Session completions and their outcomes
- System changes or discoveries
- Discord/notification message logging:
  - `YYYY-MM-DD HH:MM UTC | discord-intent | [context] - "[message excerpt]"`
  - `YYYY-MM-DD HH:MM UTC | discord-sent | [context]`

**Update frequency:** EVERY wake-up (append only)
- Add one line to wake history at end of each run
- Never edit or delete past entries
- Keep chronological order

**HARD RULE:** Append only. Never modify past entries.

**What does NOT belong here:**
- Current status (→ working-memory.md)
- Extracted patterns or principles (→ semantic-memory.md)
- Analysis or interpretation (→ semantic-memory.md)

**Archive rule:** When this file exceeds 2000 lines, archive to memory/archive/

---

## Wake History

Record of when the agent woke up and why (single line per wake-up).

Format: `date/time | type (cron, github trigger, manual) | summary of actions`

[YYYY-MM-DD HH:MM UTC] | manual | Wake #1 - Initial setup. Template initialized.

---

## Events

_Significant events logged with timestamps._

[YYYY-MM-DD HH:MM UTC] | Agent-base template initialized from vm-01-invocation architecture.
