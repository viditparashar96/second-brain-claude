---
name: status
description: Quick status overview from all connected integrations
triggers:
  - "status"
  - "what's going on"
  - "overview"
---

# Status Check

Run a quick status check across all connected integrations.

## Workflow

1. Run: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" status`
2. If Gmail is enabled: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail list --unread --limit 5`
3. If Asana is enabled: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana overdue`
4. If GitHub is enabled: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" github rate-limit`
5. Check background services:
   ```
   python3 -c "import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts'); from platform_utils import get_service_status; print(get_service_status())"
   ```
6. Summarize findings in a concise format grouped by priority (urgent / today / info). Include background service status at the end.
