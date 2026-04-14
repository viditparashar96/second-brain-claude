# Second Brain — Claude Code Plugin

AI-powered personal memory layer for Claude Code and Claude Desktop. Persistent memory, live integrations, proactive monitoring, and auto-learning from every conversation.

## Prerequisites

- **Claude Code** — installed and authenticated
- **Python 3.10+** — [python.org/downloads](https://python.org/downloads/)
  - macOS: `brew install python@3.12` or download from python.org
  - Windows: Download from python.org — **check "Add to PATH" during install**
  - Linux: `sudo apt install python3` or `sudo dnf install python3`

## Install (Team — from GitLab/GitHub)

```bash
# Step 1: Add the marketplace (one time)
/plugin marketplace add https://git.bngrenew.com/vidit.parashar/second-brain-claude-plugin

# Step 2: Install the plugin
/plugin install second-brain@blackngreen-tools

# Step 3: Run the setup wizard
/second-brain:setup
```

The setup wizard walks you through:
1. Python version check
2. Your profile (name, role, timezone)
3. Proactivity level (Observer → Partner)
4. Integration setup (Gmail, GitHub, Asana, Slack) — with guided auth
5. Claude API config (Bedrock / API key / Claude Max CLI)
6. Vault creation at `~/.second-brain/vault/`
7. Background services (macOS/Windows/Linux)

## Install (Development — local)

```bash
claude --plugin-dir /path/to/second-brain-plugin
```

## What It Does

Once installed, your Claude Code sessions automatically:
- **Load your memory** — SOUL.md, USER.md, MEMORY.md, recent logs injected at session start
- **Auto-log decisions** — Stop hook extracts decisions, action items, new entities from every conversation
- **Auto-create vault files** — Mention a new project or client naturally, a vault file appears
- **Save context before compaction** — Nothing lost in long sessions

## Skills

| Skill | What it does |
|-------|-------------|
| `/second-brain:setup` | Onboarding wizard |
| `/second-brain:status` | Quick overview from all integrations |
| `/second-brain:heartbeat` | Manual integration health check |
| `/second-brain:reflect` | Promote daily log items to long-term memory |
| `/second-brain:meeting-notes` | Structured meeting capture |
| `/second-brain:code-review` | Automated PR review sweep |
| `/second-brain:email-drafter` | Draft emails in your voice |
| `/second-brain:vault-structure` | File organization rules |
| `/second-brain:uninstall` | Clean removal |

## Agents

| Agent | Role |
|-------|------|
| `productivity-assistant` | Main agent — memory, context, coordination |
| `code-reviewer` | PR review specialist |
| `email-writer` | Email drafting with voice matching |
| `meeting-scribe` | Structured meeting notes |

## Integrations

| Integration | Auth | What you get |
|-------------|------|-------------|
| Gmail | OAuth2 | Read, search, draft (never sends) |
| GitHub | Fine-grained PAT | PRs, issues, diffs, review comments |
| Asana | PAT | Tasks, deadlines, projects |
| Slack | Bot + App tokens | Chat bot, channel summaries |

## Claude Desktop (MCP Server)

For non-technical users (HR, Sales, Management) who use Claude Desktop instead of Claude Code:

```bash
# Run once after /second-brain:setup
python3 /path/to/second-brain-plugin/scripts/setup_desktop.py
```

Then restart Claude Desktop. Available:
- **5 Resources** — SOUL.md, USER.md, MEMORY.md, HABITS.md, today's log (auto-loaded)
- **6 Prompts** — Status Check, Draft Email, Review PR, Meeting Notes, Catch Me Up, Search Knowledge
- **17 Tools** — search_memory, list_emails, draft_email, overdue_tasks, etc.

## Background Services

Installed during setup (optional). Auto-detects OS:

| Service | macOS | Windows | Linux | Schedule |
|---------|-------|---------|-------|----------|
| Heartbeat | launchd | Task Scheduler | systemd | Every 30 min |
| Vault indexer | launchd | Task Scheduler | systemd | Every 15 min |
| Daily reflection | launchd | Task Scheduler | systemd | 8:00 AM |

Check status:
```bash
python3 -c "import sys; sys.path.insert(0, 'PLUGIN_PATH/scripts'); from platform_utils import get_service_status; print(get_service_status())"
```

## Data Location

```
~/.second-brain/
├── vault/          ← Your memory (Obsidian-compatible)
├── data/           ← SQLite DBs, model cache, logs
├── .venv/          ← Plugin's Python venv (auto-managed)
├── .env            ← API tokens (never committed)
└── config.json     ← Plugin configuration
```

## Uninstall

```bash
# In Claude Code
/second-brain:uninstall

# Or manually
rm -rf ~/.second-brain          # Delete all data
/plugin uninstall second-brain  # Remove plugin
```

## Platform Support

| OS | Claude Code Plugin | Claude Desktop MCP | Background Services |
|----|-------------------|-------------------|-------------------|
| macOS | Full | Full | launchd |
| Windows | Full | Full | Task Scheduler |
| Linux | Full | Full | systemd |

## License

MIT
