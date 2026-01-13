# Episodic Memory Archive Guide

## When to Archive

Archive episodic-memory.md when it exceeds **2000 lines**.

## How to Archive

1. **Create archive file:**
   ```bash
   mv memory/episodic-memory.md memory/archive/episodic-memory-$(date +%Y%m%d).md
   ```

2. **Create fresh episodic memory:**
   - Copy the header/template from the archived file
   - Add a note: `Previous archive: episodic-memory-YYYYMMDD.md (N lines)`
   - Start fresh with wake history

3. **Update semantic memory:**
   - Before archiving, extract any patterns from the old episodic memory
   - Document patterns in semantic-memory.md with archive reference

## Archive Naming Convention

- `episodic-memory-YYYYMMDD.md` (date of archive)
- Or `episodic-memory-N.md` (sequential numbering)

## Retrieving Old Data

To find historical events:
1. Check archive files by date range
2. Use grep to search across archives:
   ```bash
   grep -r "search term" memory/archive/
   ```

## Retention Policy

- Keep all archives indefinitely (git history preserves)
- Archives are read-only reference material
- Never modify archived files
