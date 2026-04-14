---
name: reflect
description: Run daily reflection — promote important items from daily logs to MEMORY.md and archive habits
argument-hint: "[--date YYYY-MM-DD] [--dry-run]"
triggers:
  - "reflect"
  - "run reflection"
  - "promote to memory"
  - "consolidate memory"
---

# Daily Reflection

Run the memory reflection script to promote important items from daily logs to long-term memory (MEMORY.md) and archive habit checklists.

## Usage

- `/second-brain:reflect` — reflect on yesterday's log
- `/second-brain:reflect --date 2026-04-13` — reflect on a specific date
- `/second-brain:reflect --dry-run` — preview what would be promoted without writing

## Workflow

1. Parse arguments from `$ARGUMENTS` (default: yesterday, no dry-run)
2. Build the command:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_reflect.py" [--date YYYY-MM-DD] [--dry-run] [--no-llm]
   ```
3. Run it and show the output to the user
4. If not dry-run, mention that MEMORY.md and HABITS.md were updated

## What It Does

- Reads the daily log for the target date
- Uses Claude (or heuristics with `--no-llm`) to extract:
  - Key decisions → `## Key Decisions` in MEMORY.md
  - Project updates → `## Active Projects`
  - Client insights → `## Client Notes`
  - Lessons learned → `## Lessons Learned`
  - Goal progress → `## Goals`
  - Team context → `## Team Context`
- Archives the day's habit checklist to HABITS.md History section
- Creates a fresh habit checklist for today
- Warns if MEMORY.md exceeds 500 lines (needs pruning)
