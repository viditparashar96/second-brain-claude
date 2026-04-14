---
name: heartbeat
description: Run a manual heartbeat check across all integrations
triggers:
  - "heartbeat"
  - "check everything"
  - "run heartbeat"
---

# Manual Heartbeat

Run the heartbeat script to gather data from all integrations, diff against last state, and report changes.

## Workflow

1. Run: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/heartbeat.py" --force --no-llm`
2. Report the results to the user
3. If urgent items found, highlight them
