---
name: setup
description: Interactive onboarding wizard for Second Brain — configures integrations, creates vault, sets up background services
argument-hint: "[--reset]"
triggers:
  - "setup second brain"
  - "setup my second brain"
  - "onboard"
  - "initialize second brain"
---

# Second Brain Setup Wizard

Interactive onboarding that configures your AI Second Brain step by step.

**Data directory:** `~/.second-brain/`

## Prerequisites

Before starting, verify:
1. **Python 3.10+** — Run: `python3 --version` (or `python --version` on Windows)
   - If not installed: guide the user to https://python.org/downloads/
   - On macOS: `brew install python@3.12` or download from python.org
   - On Windows: Download from python.org, CHECK "Add to PATH" during install
2. **Claude Code** — Must be installed and authenticated

## Workflow

### Step 0: Detect OS and verify Python

Run: `python3 -c "import sys, platform; print(f'{platform.system()}|{sys.version_info.major}.{sys.version_info.minor}')"`

Parse the output:
- First part = OS: `Darwin` (macOS), `Windows`, or `Linux`
- Second part = Python version: must be 3.10+

If Python not found or <3.10, tell the user:
- macOS: "Install Python: `brew install python@3.12` or download from https://python.org/downloads/"
- Windows: "Download Python from https://python.org/downloads/ — IMPORTANT: check 'Add to PATH' during install"
- Linux: "Install Python: `sudo apt install python3` or `sudo dnf install python3`"

Stop setup until Python is available.

### Step 1: Check if already set up

Read `~/.second-brain/config.json`. If it exists and `setup_complete` is true, tell the user:
"Second Brain is already configured. Run `/second-brain:setup --reset` to reconfigure."

If `$ARGUMENTS` contains `--reset`, delete `~/.second-brain/config.json` and proceed.

### Step 2: Gather user profile

Ask the user (one question at a time):

1. **What's your name?**
2. **Your role?** (Developer / Sales / HR / Management / Other)
3. **Your timezone?** (e.g., IST, EST, PST, UTC)
4. **How proactive should I be?**
   - Observer — Notify only, never take action
   - Advisor — Draft things for review, but never send
   - Assistant — Act on low-risk items, ask for high-risk
   - Partner — Act autonomously, ask only for irreversible actions

### Step 3: Select integrations

Ask: **Which integrations do you want to connect?** (select all that apply)

- [ ] Gmail (email reading, drafting)
- [ ] GitHub (PRs, issues, code review)
- [ ] Asana (tasks, deadlines)
- [ ] Slack (chat bot, channel summaries)

### Step 4: Configure each selected integration

**For Gmail:**
1. "Do you have a Google Cloud project with Gmail API enabled? (yes/no)"
2. If no: Walk through the steps (create project → enable API → OAuth consent → download credentials.json)
3. "Place your credentials.json at `~/.second-brain/data/credentials/gmail/credentials.json`"
4. Verify it exists, then run the OAuth flow: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail list --limit 1`
5. If successful: "Gmail connected!"

**For GitHub:**
1. "Paste your GitHub Personal Access Token (fine-grained, with Contents:read + PRs:read/write + Issues:read/write):"
2. Save to `~/.second-brain/.env` as `GITHUB_TOKEN=<token>`
3. Verify: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" github rate-limit`
4. If successful: "GitHub connected!"

**For Asana:**
1. "Paste your Asana Personal Access Token (from app.asana.com/0/developer-console):"
2. Save to `~/.second-brain/.env` as `ASANA_TOKEN=<token>`
3. Verify: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana projects`
4. If successful: "Asana connected!"

**For Slack:**
1. Walk through Slack app creation (api.slack.com/apps → scopes → Socket Mode → events)
2. "Paste your Bot Token (xoxb-...):" → save as `SLACK_BOT_TOKEN`
3. "Paste your App Token (xapp-...):" → save as `SLACK_APP_TOKEN`
4. Save both to `~/.second-brain/.env`

### Step 5: Configure Claude API

Ask: "How do you access Claude?"
- **AWS Bedrock** → ask for AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
- **Anthropic API Key** → ask for ANTHROPIC_API_KEY
- **Claude Max (CLI)** → no key needed

Save to `~/.second-brain/.env`.

### Step 6: Create vault structure

Create the directory structure at `~/.second-brain/vault/`:
```
vault/
├── SOUL.md          ← populate from templates/ with user's name and role
├── USER.md          ← populate with integration config
├── MEMORY.md        ← empty sections template
├── HABITS.md        ← default pillars based on role
├── HEARTBEAT.md     ← monitoring checklist based on enabled integrations
├── daily/
├── meetings/
├── projects/
├── clients/
├── team/
├── research/
├── content/
└── drafts/{active,sent,expired}/
```

Use template files from `${CLAUDE_PLUGIN_ROOT}/templates/` and customize based on user answers.

### Step 7: Install dependencies

The plugin manages its own Python virtual environment. On first run, it auto-creates `~/.second-brain/.venv/` and installs all dependencies. This happens automatically when scripts are called — no manual pip install needed.

If the user reports import errors, run:
```bash
python3 -m venv ~/.second-brain/.venv && ~/.second-brain/.venv/bin/pip install -r "${CLAUDE_PLUGIN_ROOT}/requirements.txt"
```

### Step 8: Index vault

Run: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_index.py"`

### Step 8: Save config

Write `~/.second-brain/config.json`:
```json
{
  "setup_complete": true,
  "user": { "name": "...", "role": "...", "timezone": "..." },
  "integrations": {
    "gmail": { "enabled": true },
    "github": { "enabled": true },
    "asana": { "enabled": false },
    "slack": { "enabled": false }
  },
  "proactivity": "assistant",
  "claude_api": "bedrock"
}
```

### Step 9: Install background services

Ask: "Want to install background services? They run silently in the background:"
- Heartbeat (checks integrations every 30 min, sends notifications)
- Vault indexer (re-indexes for search every 15 min)
- Daily reflection (promotes daily log items to MEMORY.md at 8am)

If yes, run:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from platform_utils import install_background_services
venv_py = str('{HOME}/.second-brain/.venv/bin/python3')
import platform
if platform.system() == 'Windows':
    venv_py = str('{HOME}/.second-brain/.venv/Scripts/python.exe')
print(install_background_services('${CLAUDE_PLUGIN_ROOT}', '{HOME}/.second-brain', venv_py))
"
```

This auto-detects the OS:
- **macOS**: installs launchd agents
- **Windows**: creates Task Scheduler entries
- **Linux**: creates systemd user timers

If the user declines, tell them they can run scripts manually or install later.

### Step 10: Confirm completion

Print:
```
Second Brain setup complete!

Your vault: ~/.second-brain/vault/
Your config: ~/.second-brain/config.json

What's running:
- SessionStart hook: loads memory into every conversation (automatic)
- Stop hook: auto-logs decisions and action items (automatic)
- Background services: heartbeat, indexer, reflection (if installed)

Next steps:
- Open ~/.second-brain/vault/ in Obsidian for graph view
- Try: /second-brain:status
- Try: "show me my open PRs"
- Try: "draft an email to..."
- Just work normally — decisions and action items are auto-logged
```

## Rules

- Ask ONE question at a time — don't overwhelm the user
- Validate each integration works before moving to the next
- Never store tokens in vault markdown — only in ~/.second-brain/.env
- If any step fails, explain the error and offer to retry or skip
