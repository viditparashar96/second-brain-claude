---
description: "Create an Architecture Decision Record — structured trade-off analysis with weighted scoring"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# Architecture Decision Record

You are a senior architect. Make a rigorous, documented technical decision.

## Decision Topic

$ARGUMENTS

## Step 1: Frame

Read project and org context:
```bash
ls docs/adrs/ 2>/dev/null
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
cat ~/.second-brain/vault/ORG.md 2>/dev/null
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "$ARGUMENTS" --top-k 5 2>/dev/null
```

**Ultrathink** — Define:
1. What exactly needs to be decided?
2. Which product(s) are affected? (read from PRODUCTS.md)
3. Decision drivers (weighted by importance)
4. Type 1 (irreversible) or Type 2 (reversible)?
5. Prior ADRs that constrain this?

Present framing. **Wait for confirmation.**

## Step 2: Evaluate Options

Build a weighted comparison matrix:

```
| Criteria (weight)      | Option A | Option B | Option C |
|------------------------|----------|----------|----------|
| {driver1} ({weight}%)  | ★★★★☆   | ★★★☆☆   | ★★★★★   |
| Weighted Score         | X.XX     | X.XX     | X.XX     |
```

For each option: pros, cons, hidden costs, top 3 risks with mitigations.

## Step 3: Recommend

Present recommendation with:
- Which option and WHY
- Trade-offs accepted / rejected
- Impact on affected products

**Wait for approval.**

## Step 4: Document (LOCAL FIRST)

```bash
mkdir -p docs/adrs
NEXT=$(( $(ls docs/adrs/ 2>/dev/null | wc -l) + 1 ))
```

Save to `docs/adrs/ADR-$(printf '%03d' $NEXT)-{slug}.md`:

```markdown
---
adr_id: "ADR-{NNN}"
title: "{title}"
date: "{YYYY-MM-DD}"
status: "accepted"
decision_type: "{Type 1/2}"
products: ["{product}"]
---

# ADR-{NNN}: {title}

## Status
Accepted — {date}

## Context
{what situation prompted this, org/product context}

## Decision Drivers
{numbered, weighted}

## Options Considered
### Option A: {name}
{pros, cons, risks}
### Option B: {name}
{pros, cons, risks}

## Decision
{what and why, reference matrix}

## Consequences
### Positive
### Negative
### Neutral

## Review Trigger
Revisit if:
- {condition}
```

Log summary to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('ADR: {title} — Decided: {decision}. Products: {list}.')
"
```

## Rules

- Weighted criteria, not gut feeling
- Every option gets fair analysis
- Type 1 = full ADR; Type 2 = lightweight
- Save to LOCAL project docs/ first
- Log summary to memory second
