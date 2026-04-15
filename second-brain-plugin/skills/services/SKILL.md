---
name: services
description: Manage Second Brain background services — install, uninstall, status, restart
argument-hint: "{install|uninstall|status|restart}"
triggers:
  - "install background services"
  - "install services"
  - "start services"
  - "stop services"
  - "service status"
  - "background services"
  - "restart services"
---

# Background Services Manager

Manage Second Brain background services (heartbeat, vault indexer, daily reflection).

## Usage

- `/second-brain:services install` — Install and start all services
- `/second-brain:services uninstall` — Stop and remove all services
- `/second-brain:services status` — Check which services are running
- `/second-brain:services restart` — Restart all services

## Workflow

### Parse the action from `$ARGUMENTS`

Default to `status` if no argument given.

### For `install`:

```bash
python3 -c "
import sys, os, platform
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from platform_utils import install_background_services
sb_home = os.path.expanduser('~/.second-brain')
venv_py = os.path.join(sb_home, '.venv', 'bin', 'python3')
if platform.system() == 'Windows':
    venv_py = os.path.join(sb_home, '.venv', 'Scripts', 'python.exe')
result = install_background_services('${CLAUDE_PLUGIN_ROOT}', sb_home, venv_py)
print(result)
"
```

Tell the user what was installed and on which OS (macOS → launchd, Windows → Task Scheduler, Linux → systemd).

### For `uninstall`:

```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from platform_utils import uninstall_background_services
print(uninstall_background_services())
"
```

### For `status`:

```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from platform_utils import get_service_status
print(get_service_status())
"
```

### For `restart`:

Run uninstall then install.

## Services

| Service | What it does | Schedule |
|---------|-------------|----------|
| Heartbeat | Checks Gmail, GitHub, Asana for changes, sends notifications | Every 30 min |
| Vault Indexer | Re-indexes vault for RAG search | Every 15 min |
| Daily Reflection | Promotes daily log items to MEMORY.md, archives habits | 8:00 AM daily |
