# Second Brain — AI Memory & Productivity System

AI-powered personal memory layer for Claude Code and Claude Desktop. Persistent cloud memory, live integrations (Gmail, GitHub, Asana, Google Calendar), 49 skills, 4 agents, and 22 MCP prompts.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    CLOUD (for everyone)                       │
│                                                               │
│  MCP Server: https://second-brain-cloud-app.azurewebsites.net│
│  Dashboard:  (same URL, port +1)                              │
│  Database:   NeonDB (Postgres + pgvector)                     │
│  Reflection: AWS Bedrock (Claude Haiku)                       │
│  Repo:       github.com/viditparashar96/second-brain-cloud    │
│                                                               │
│  22 MCP tools │ 22 MCP prompts │ 7 MCP resources              │
│  Per-user vault │ Hybrid RAG search │ Auto-memory              │
└──────────────────────────┬───────────────────────────────────┘
                           │
              MCP over HTTPS (?key=sb_xxx)
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   Claude Desktop    Claude Code      claude.ai
   (HR, Sales, Ops)  + This Plugin    (web users)
                     (Engineers)
```

## Cloud MCP Server

The cloud MCP server provides shared memory, integrations, and prompts for all users. No local install needed — just connect with your unique URL.

**Production URL:**
```
https://second-brain-cloud-app.azurewebsites.net/mcp?key=YOUR_API_KEY
```

**Cloud Repo:** [github.com/viditparashar96/second-brain-cloud](https://github.com/viditparashar96/second-brain-cloud) (private)

### What the Cloud Provides

| Feature | Count | Details |
|---------|-------|---------|
| **MCP Tools** | 22 | Vault CRUD, search, logging, Gmail, GitHub, Asana, GCal, status |
| **MCP Prompts** | 22 | Core, HR, Sales, Product, Ops, Org workflows |
| **MCP Resources** | 7 | SOUL, USER, ORG, PRODUCTS, MEMORY, HABITS, Today's log |
| **Search** | Hybrid RAG | pgvector (semantic) + PostgreSQL FTS (keyword), 70/30 merge |
| **Memory** | Auto | SOUL.md rules make Claude log everything important |
| **Reflection** | Daily | Bedrock extracts decisions/actions → MEMORY.md |

## Connect: Claude Code (Engineers)

### Step 1: Install Plugin (for skills + agents)

```bash
# Add marketplace
/plugin marketplace add https://github.com/viditparashar96/second-brain-claude

# Install
/plugin install second-brain@blackngreen-tools
```

### Step 2: Connect Cloud Memory (global — works in every project)

```bash
claude mcp add second-brain-cloud "https://second-brain-cloud-app.azurewebsites.net/mcp?key=YOUR_API_KEY" -t http -s user
```

Get your API key from the admin dashboard.

### Step 3: Use It

```
# Skills (from plugin)
/eng-plan build GPS tracking for School Cab
/eng-code-review
/meeting-notes

# Cloud memory (from MCP — works automatically)
"search my memory for Nexiva"
"log a note: decided to use pgvector"
"what's on my calendar today?"
"run daily reflection"
```

Skills call cloud MCP tools automatically — all decisions, meetings, and outcomes are logged to your cloud vault.

## Connect: Claude Desktop (HR, Sales, Ops, Product)

### Step 1: Admin Creates User

Admin creates user on the dashboard or via API. Each user gets a unique API key.

### Step 2: Add to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "second-brain": {
      "command": "npx",
      "args": ["mcp-remote", "https://second-brain-cloud-app.azurewebsites.net/mcp?key=YOUR_API_KEY"]
    }
  }
}
```

Restart Claude Desktop (Cmd+Q → reopen).

### Step 3: Use It

- Click **"+"** button → see 22 prompts (Status Check, Draft Email, Deal Prep, Meeting Notes, etc.)
- Just chat — Claude auto-uses tools (search memory, check tasks, draft emails)
- Memory builds automatically — Claude logs decisions, creates vault files, tracks projects

## Connect: claude.ai (Web)

Add as a Custom Connector in Settings → Connectors:
```
URL: https://second-brain-cloud-app.azurewebsites.net/mcp?key=YOUR_API_KEY
```

## Plugin Skills (49)

Available in Claude Code via `/skill-name`:

### Engineering (14)
| Skill | What it does |
|-------|-------------|
| `/eng-plan` | Implementation planner with phases, estimates, gates |
| `/eng-code-review` | Multi-pass code review (correctness, security, performance) |
| `/eng-debug-rca` | Hypothesis-driven debugging and root cause analysis |
| `/eng-architecture-decision` | ADR creator with trade-off analysis |
| `/eng-api-design` | API design review and OpenAPI spec generation |
| `/eng-deploy-checklist` | Pre/post deploy validation and rollback procedures |
| `/eng-incident-response` | Multi-phase incident response with diagnostics |
| `/eng-release-notes` | Git-driven release note generator |
| `/eng-sprint-retro` | Sprint retrospective facilitator |
| `/eng-tech-debt` | Tech debt tracker with business-impact scoring |
| `/eng-dev-onboarding` | Developer onboarding plan generator |
| `/code-review` | Quick PR review sweep |
| `/email-drafter` | Draft emails in your voice |
| `/meeting-notes` | Structured meeting capture with action items |

### Product (7)
`/product-prd-drafter` · `/product-manager` · `/product-feedback-synthesis` · `/product-stakeholder-update` · `/product-one-on-one` · `/product-okr-tracker` · `/meeting-prep`

### Sales (6)
`/sales-deal-prep` · `/sales-proposal-drafter` · `/sales-follow-up` · `/sales-competitive-analysis` · `/sales-pipeline-review`

### HR (6)
`/hr-interview-feedback` · `/hr-onboarding-checklist` · `/hr-performance-review` · `/hr-policy-lookup` · `/hr-pto-tracker`

### Operations (5)
`/ops-compliance-checklist` · `/ops-process-audit` · `/ops-resource-allocation` · `/ops-sop-creator` · `/ops-vendor-management`

### Core
`/second-brain:setup` · `/second-brain:status` · `/second-brain:heartbeat` · `/second-brain:reflect` · `/second-brain:memory` · `/second-brain:services` · `/second-brain:uninstall` · `/org-manager` · `/vault-structure`

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
| Google Calendar | OAuth2 (shared with Gmail) | Events, meetings, attendees |

Integrations are connected per-user via the admin dashboard. Credentials stored encrypted in NeonDB.

## How Memory Builds Automatically

```
User chats with Claude (Desktop or Code)
    │
    ▼
SOUL.md loaded → Claude reads auto-memory rules
    │
    ├── Decisions → log_note → embedded in pgvector → searchable
    ├── Meetings → create_vault_file → indexed → searchable
    ├── New clients → create_vault_file → indexed → searchable
    ├── Action items → log_note → embedded → searchable
    │
    └── Daily 8AM → Bedrock reflection → MEMORY.md (permanent knowledge)
```

No commands needed. Claude follows SOUL.md rules and auto-logs everything important.

## Infrastructure

| Service | URL / Location | Cost |
|---------|---------------|------|
| Cloud MCP Server | `second-brain-cloud-app.azurewebsites.net` | Azure Free (F1) |
| Database | NeonDB (ap-southeast-1) | Free tier |
| Reflection LLM | AWS Bedrock (us-east-1) Claude Haiku | ~$0.02/mo |
| Plugin repo | `github.com/viditparashar96/second-brain-claude` | Free |
| Cloud repo | `github.com/viditparashar96/second-brain-cloud` | Free (private) |

## Platform Support

| OS | Claude Code + Plugin | Claude Desktop (Cloud MCP) | claude.ai (Cloud MCP) |
|----|---------------------|---------------------------|----------------------|
| macOS | Full | Full | Full |
| Windows | Full | Full | Full |
| Linux | Full | Full | Full |

## License

MIT
