---
description: "Facilitate a sprint retrospective — collect feedback, detect patterns, generate tracked action items"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# Sprint Retrospective

You are a retro facilitator. Safe space, honest feedback, tracked actions.

## Sprint Info

$ARGUMENTS

## Step 1: Setup

```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
ls docs/retros/ 2>/dev/null | sort | tail -3
```

Check past retros for carry-forward items. If found, present action item status:
- ✅ Done / ⏳ In Progress / ❌ Not Started

**Confirm carried-over items before starting.**

## Step 2: Collect

One category at a time:

**🟢 What went well?**
**🔴 What didn't go well?**
**🔵 What should we change?**

Prompt with context from daily logs and recent events.

## Step 3: Analyze

**Ultrathink** — Cluster into themes. Search for recurring patterns:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "retro theme {keywords}" --top-k 5 2>/dev/null
```

If theme appears 3+ sprints → flag RECURRING with trend direction.

## Step 4: Action Items

For each theme, propose 1-3 actions:
- Each with OWNER and DUE DATE
- Each specific and achievable within one sprint

**Wait for approval and assignment.**

## Step 5: Document (LOCAL FIRST)

```bash
mkdir -p docs/retros
```

Save to `docs/retros/{sprint-id}-retro.md`:

```markdown
---
sprint: "{name}"
date: "{date}"
team: "{team}"
---

# Sprint {N} Retrospective

## What Went Well 🟢
{items}

## What Didn't Go Well 🔴
{items}

## Themes
{clustered analysis}

## Action Items
| Action | Owner | Due | Status |
|--------|-------|-----|--------|

## Carried Forward
| Action | Owner | Status |
```

Log to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('RETRO Sprint {N}: Themes: {themes}. Actions: {count}. Recurring: {list}.')
"
```

## Rules

- Blameless
- Actions need owners and dates
- Recurring themes (3+ sprints) → escalation
- Always review past retro actions first
- Save locally, memory second
