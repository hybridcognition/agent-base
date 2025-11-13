# Episodic Memory

Append-only time-stamped event log. Archive to memory/archive/ when >2000 lines.

**Format**: `YYYY-MM-DD HH:MM UTC | type | description`

**Entry Types**: wake-cron, wake-telegram, decision, discovery, problem, system-change

---

2025-11-10 00:00 UTC | system-change | Initial memory structure created
2025-11-13 00:00 UTC | wake-telegram | Agent wake cycle triggered - found 4 unprocessed Telegram messages
2025-11-13 00:01 UTC | decision | Processed 4 "Test" messages from chat_id 429153217, responded with agent introduction and capabilities overview
2025-11-13 (current) | wake-telegram | Agent wake cycle triggered - found 1 unprocessed message
2025-11-13 (current) | decision | Processed operational status query "Are you operational?", confirmed all systems green
