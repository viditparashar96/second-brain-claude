---
name: uninstall
description: Remove Second Brain — stops background services, optionally deletes vault and data
argument-hint: "[--keep-data]"
triggers:
  - "uninstall second brain"
  - "remove second brain"
---

# Uninstall Second Brain

Cleanly removes Second Brain services and optionally all data.

## Workflow

### Step 1: Stop background services

Run:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from platform_utils import uninstall_background_services
print(uninstall_background_services())
"
```

Tell the user: "Background services stopped and removed."

### Step 2: Remove Claude Desktop config (if configured)

Run:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup_desktop.py" --uninstall
```

### Step 3: Ask about data

If `$ARGUMENTS` contains `--keep-data`:
  - Skip deletion, tell user "Your vault is preserved at ~/.second-brain/"
  - Done.

Otherwise ask: "Do you want to delete your vault and all data? This includes:"
- Memory vault (projects, clients, team, meeting notes, daily logs)
- API tokens (.env)
- Search database
- Configuration

**This cannot be undone.**

Options:
1. **Delete everything** — `rm -rf ~/.second-brain`
2. **Keep vault, delete the rest** — Keep `~/.second-brain/vault/`, delete `~/.second-brain/data/`, `.env`, `config.json`
3. **Keep everything** — Just unload the plugin, data stays

### Step 4: Confirm

Tell the user:
```
Second Brain uninstalled.

What was removed:
- Background services (heartbeat, indexer, reflection)
- Claude Desktop MCP config (if configured)
- [Data status based on their choice]

To reinstall: /plugin install second-brain@your-marketplace
Then: /second-brain:setup
```
