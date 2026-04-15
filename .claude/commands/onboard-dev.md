---
description: "Generate a personalized developer onboarding plan — product-specific setup, starter tasks, 30-60-90 milestones"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# Developer Onboarding

Generate a personalized onboarding plan.

## Developer Info

$ARGUMENTS

(Expected: name, product, role, level)

## Step 1: Context

```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
cat ~/.second-brain/vault/ORG.md 2>/dev/null
ls docs/ README.md CONTRIBUTING.md 2>/dev/null
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "onboarding developer" --top-k 5 2>/dev/null
```

**Ultrathink** — From PRODUCTS.md, dynamically extract:
- The assigned product's tech stack
- Setup requirements for each component
- Known issues and active development areas
- Product dependencies

## Step 2: Generate Plan

### Week 1: Environment & Orientation
- Day 1: HR onboarding, access, Slack, meet buddy
- Day 2: Dev environment (generate setup steps from product tech stack)
- Day 3: Codebase walkthrough with buddy
- Day 4-5: First contribution (level-adjusted)

### 30-Day: Productive Contributor
- Build/run full stack, 3-5 PRs, debug independently

### 60-Day: Independent Contributor
- Design features, review PRs, understand competitive landscape

### 90-Day: Full Team Member
- Architecture proposals, mentor others, ship significant feature

### Starter Tasks (level-adjusted)
Generate 5 progressive tasks:
- Junior: fix bug → add test → small feature
- Mid: add tests → implement feature → review PR
- Senior: review PR → propose improvement → lead feature

## Step 3: Save (LOCAL FIRST)

```bash
mkdir -p docs/onboarding
```

Save to `docs/onboarding/{name-slug}.md`

Log to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('ONBOARDING: {name} joined {product} as {role} ({level}).')
"
```

## Rules

- Tech stack from PRODUCTS.md — never hardcode
- Personalized by role, level, AND product
- Starter tasks are curated and progressive
- Include product competitive context
- Save locally, memory second
