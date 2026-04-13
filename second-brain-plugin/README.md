# Second Brain — Claude Code Plugin

AI-powered personal productivity system with persistent memory, live integrations, proactive monitoring, and an MCP server for Claude Desktop.

## Install

```bash
# From marketplace (when published)
/plugin install second-brain

# From local directory (for development)
claude --plugin-dir ./second-brain-plugin
```

## Quick Start

```
/second-brain:setup
```

The setup wizard walks you through:
1. Your profile (name, role, timezone)
2. Proactivity level (Observer → Partner)
3. Integration setup (Gmail, GitHub, Asana, Slack)
4. API keys (AWS Bedrock or Anthropic direct)
5. Vault creation at `~/.second-brain/vault/`

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `/second-brain:setup` | "setup second brain" | Onboarding wizard |
| `/second-brain:status` | "status" | Quick overview from all integrations |
| `/second-brain:heartbeat` | "run heartbeat" | Manual heartbeat check |
| `/second-brain:meeting-notes` | "meeting notes" | Capture structured meeting notes |
| `/second-brain:code-review` | "review this PR" | Initial PR review sweep |
| `/second-brain:email-drafter` | "draft an email" | Draft emails in your voice |
| `/second-brain:vault-structure` | Auto | File organization rules |

## Agents

| Agent | Role |
|-------|------|
| `productivity-assistant` | Main agent — memory, context, coordination |
| `code-reviewer` | PR review specialist |
| `email-writer` | Email drafting in your voice |
| `meeting-scribe` | Structured meeting notes |

## MCP Server (Claude Desktop)

The plugin includes an MCP server that works with Claude Desktop:

**Tools available:**
- `search_memory` — RAG search across your vault
- `list_emails` / `read_email` / `draft_email` — Gmail
- `list_tasks` / `overdue_tasks` / `upcoming_tasks` — Asana
- `list_prs` / `pr_diff` — GitHub
- `get_status` — Integration overview
- `log_note` — Save to daily vault log
- `index_vault` — Re-index for search

## Architecture

```
~/.second-brain/              ← Your data (never in the plugin)
├── vault/                    ← Obsidian-compatible markdown vault
│   ├── SOUL.md, USER.md, MEMORY.md, HABITS.md
│   ├── daily/, meetings/, projects/, clients/, team/
│   └── drafts/{active,sent,expired}/
├── data/                     ← SQLite DBs, model cache, logs
├── .env                      ← API tokens (never committed)
└── config.json               ← Plugin configuration

second-brain-plugin/          ← The plugin (installable, shareable)
├── .claude-plugin/plugin.json
├── skills/                   ← 7 skills
├── agents/                   ← 4 agents
├── hooks/hooks.json          ← Lifecycle hooks
├── scripts/                  ← Python engine
├── mcp-server/server.py      ← MCP server for Claude Desktop
├── templates/                ← Vault file templates
└── .mcp.json                 ← MCP config
```

## Integrations

| Integration | Auth | What you get |
|-------------|------|-------------|
| Gmail | OAuth2 | Read, search, draft (never send) |
| GitHub | Fine-grained PAT | PRs, issues, diffs, review comments |
| Asana | PAT | Tasks, deadlines, projects |
| Slack | Bot + App tokens | Chat bot, channel summaries |

## Requirements

- Python 3.10+
- Claude Code (latest)
- macOS / Linux / Windows

```bash
pip install -r requirements.txt
```

## License

MIT
