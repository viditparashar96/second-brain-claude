---
description: "Track and prioritize tech debt — business-impact scoring, payoff planning, trend reporting"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# Tech Debt Manager

Catalog, score, and prioritize technical debt.

## Command

$ARGUMENTS

(Use: `add {description}`, `list`, `prioritize`, `report`)

## Context

```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
cat ~/.second-brain/vault/ORG.md 2>/dev/null
```

## Add

Score 1-5 on each:
- Reliability risk
- Development velocity impact
- Customer impact
- Security risk
- Scaling blocker

Effort 1-5:
- Complexity, Scope, Risk of fix

**Priority = (avg_impact × 10) / avg_effort**
- ≥15: 🔴 Critical
- 10-15: 🟠 High
- 5-10: 🟡 Medium
- <5: 🔵 Low

Save to LOCAL project:
```bash
mkdir -p docs/tech-debt
```

`docs/tech-debt/{slug}.md`:
```markdown
---
title: "{title}"
product: "{product}"
type: "{design|code|dependency|infra|docs|test}"
severity: "{level}"
score: {N}
date: "{date}"
status: "open"
---

# Tech Debt: {title}

## Description
## Business Impact
## Proposed Solution
## Effort Estimate
```

## List / Prioritize

```bash
find docs/tech-debt/ -name "*.md" 2>/dev/null
```

Sort by score. Cross-reference ORG.md strategic priorities — debt blocking priorities gets auto-escalated.

## Report

Generate leadership summary: totals by severity, strategic blockers, quarterly trend.

Log to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('TECH DEBT: {action} — {product} — {title} — Score: {score}.')
"
```

## Rules

- Business-impact scoring, not just technical severity
- Debt blocking strategic priorities gets auto-escalated
- Save locally, memory second
