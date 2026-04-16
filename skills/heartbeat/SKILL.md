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

1. Run: `Use the `get_status` MCP tool
2. Report the results to the user
3. If urgent items found, highlight them
