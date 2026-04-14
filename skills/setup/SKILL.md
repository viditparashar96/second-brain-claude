---
name: setup
description: Interactive onboarding for Second Brain — launches a local dashboard to configure profile and integrations in one click
argument-hint: "[--reset] [--text]"
triggers:
  - "setup second brain"
  - "setup my second brain"
  - "onboard"
  - "initialize second brain"
---

# Second Brain Setup

Launches a local web dashboard at `localhost:3141` for one-click profile and integration setup.

**Data directory:** `~/.second-brain/`

## Prerequisites

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

### Step 2: Launch Setup Dashboard

If `$ARGUMENTS` does NOT contain `--text`:

1. Launch the dashboard server:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup_dashboard/launch.py"
   ```

2. This will:
   - Create a venv at `~/.second-brain/.venv/` if needed
   - Install all dependencies automatically
   - Open `http://localhost:3141` in the user's browser
   - The dashboard handles: profile (name, role, timezone, proactivity), integrations (Gmail, Google Calendar, GitHub, Asana), background services

3. Tell the user:
   ```
   Setup dashboard is opening in your browser at http://localhost:3141

   Fill in your profile, connect your integrations, and click "Complete Setup".
   The server will shut down automatically when you're done.

   If the browser didn't open, visit http://localhost:3141 manually.
   ```

4. Wait for the server process to finish (it auto-exits after setup completes).

5. Verify setup succeeded by reading `~/.second-brain/config.json` and checking `setup_complete` is true.

6. Print completion message:
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
   - Try: "what's on my calendar today?"
   - Just work normally — decisions and action items are auto-logged
   ```

### Fallback: Text-Based Setup (--text flag or no browser)

If `$ARGUMENTS` contains `--text`, OR if the dashboard fails to launch, fall back to the interactive text wizard:

**Step 2t: Gather user profile**

Ask the user (one question at a time):

1. **What's your name?**
2. **Your role?** (Developer / Sales / HR / Management / Other)
3. **Your timezone?** (e.g., IST, EST, PST, UTC)
4. **How proactive should I be?**
   - Observer — Notify only, never take action
   - Advisor — Draft things for review, but never send
   - Assistant — Act on low-risk items, ask for high-risk
   - Partner — Act autonomously, ask only for irreversible actions

**Step 3t: Select integrations**

Ask: **Which integrations do you want to connect?** (select all that apply)

- [ ] Gmail (email reading, drafting)
- [ ] Google Calendar (meeting prep, scheduling)
- [ ] GitHub (PRs, issues, code review)
- [ ] Asana (tasks, deadlines)

**Step 4t: Configure each selected integration**

**For Gmail + Google Calendar:**
1. "Do you have a Google Cloud project with Gmail API and Calendar API enabled? (yes/no)"
2. If no: Walk through the steps (create project → enable APIs → OAuth consent → download credentials.json)
3. "Place your credentials.json at `~/.second-brain/data/credentials/gmail/credentials.json`"
4. Verify it exists, then run the OAuth flow: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail list --limit 1`
5. If successful: "Gmail + Calendar connected!"

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

**Step 5t: Configure Claude API**

Ask: "How do you access Claude?"
- **AWS Bedrock** → ask for AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
- **Anthropic API Key** → ask for ANTHROPIC_API_KEY
- **Claude Max (CLI)** → no key needed

Save to `~/.second-brain/.env`.

**Step 6t: Create vault + finish**

Create vault structure, install deps, index, save config — same as dashboard's "Complete Setup" flow.

Run:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from config import ensure_dirs, save_config
ensure_dirs()
"
```

**Step 7: Deploy Organization & Product Context (automatic)**

Copy the pre-filled ORG.md and PRODUCTS.md from plugin templates to the vault. These contain the organization's company profile and full product registry — no user input needed.

```bash
# Copy org and product files if they don't already exist in vault
for file in ORG.md PRODUCTS.md; do
  if [ ! -f ~/.second-brain/vault/$file ]; then
    cp "${CLAUDE_PLUGIN_ROOT}/templates/$file" ~/.second-brain/vault/$file
    echo "Deployed $file to vault"
  fi
done
```

This ensures every team member who installs the plugin automatically gets:
- **ORG.md** — Company profile, departments, strategic priorities
- **PRODUCTS.md** — Full product registry (Nexiva, EVA, Voxa, MobiBattle, VAS, Digital Services, Medical Scribe, School Cab)

These files are injected into every session and every skill has access to this context.

## Rules

- Ask ONE question at a time in text mode — don't overwhelm the user
- Validate each integration works before moving to the next
- Never store tokens in vault markdown — only in ~/.second-brain/.env
- If any step fails, explain the error and offer to retry or skip
- Dashboard is always preferred over text mode when a browser is available
