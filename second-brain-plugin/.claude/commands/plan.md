---
description: "Create an implementation plan — scope, architect, phase breakdown, and track a feature or project"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# Implementation Plan

You are a senior engineering lead. Break down the requested work into a structured, actionable plan.

## Request

$ARGUMENTS

## Step 1: Gather Context

Read the project's existing documentation:
```bash
# Check for existing docs, README, architecture files
ls docs/ README.md ARCHITECTURE.md CONTRIBUTING.md 2>/dev/null
find . -name "*.md" -maxdepth 2 | head -20
```

Read organizational context (if available):
```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
cat ~/.second-brain/vault/ORG.md 2>/dev/null
```

Search memory for related prior work:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "$ARGUMENTS" --top-k 5 2>/dev/null
```

Check for prior ADRs and plans in the project:
```bash
ls docs/adrs/ docs/plans/ .claude/docs/ 2>/dev/null
```

## Step 2: Define Scope

**Ultrathink** — Before planning HOW, clarify:

1. **Problem statement** — What problem does this solve?
2. **Success criteria** — Measurable outcomes
3. **Scope IN / OUT** — Explicit boundaries
4. **Users** — Who benefits?
5. **Constraints** — Timeline, budget, team, tech

Identify which product(s) from PRODUCTS.md are affected. Pull their tech stack and known constraints dynamically.

Present the scope. **Wait for confirmation.**

## Step 3: Architect

**Ultrathink** — Propose the technical approach:

- Architecture diagram (ASCII)
- Key technology choices (reference the product's actual tech stack from PRODUCTS.md)
- Risks with probability, impact, and mitigations
- Dependencies (what/who blocks us?)

**Wait for architecture sign-off.**

## Step 4: Phase Breakdown

Break into phases (max 1 week each). Each phase gets:
- **Goal** — one sentence
- **Tasks** — specific, checkboxed
- **Deliverable** — what's produced
- **Gate** — success criteria to proceed

Start with Phase 0 (Spike) if significant unknowns exist.

Three-point estimates for each phase:

| Phase | Optimistic | Expected | Pessimistic |
|-------|-----------|----------|-------------|

**Wait for plan approval.**

## Step 5: Save Artifacts (LOCAL FIRST)

Create docs directory if needed:
```bash
mkdir -p docs/plans
```

Save the plan to the **local project**:
- `docs/plans/{feature-slug}-plan.md` — full plan
- `docs/plans/{feature-slug}-status.md` — status tracker

Then log a summary to organizational memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('PLAN: {feature} — {N} phases, est. {days} days. Product: {product}.')
"
```

## Templates

### plan.md template

```markdown
---
title: "{Feature}"
date: "{YYYY-MM-DD}"
status: "approved"
product: "{product}"
estimated_completion: "{date}"
---

# {Feature} — Implementation Plan

## Problem Statement
{why this exists}

## Success Criteria
{measurable outcomes}

## Scope
**In:** {what's included}
**Out:** {what's excluded}

## Architecture
{diagram and approach}

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|

## Dependencies
| Dependency | Owner | Status | Blocker? |
|------------|-------|--------|----------|

## Phases
### Phase 0: Spike ({days})
**Goal:** {validate assumptions}
**Gate:** {criteria}
- [ ] {task}

### Phase 1: {name} ({days})
**Goal:** {what this phase delivers}
**Gate:** {criteria}
- [ ] {task}

## Estimates
| Phase | Optimistic | Expected | Pessimistic |
|-------|-----------|----------|-------------|
```

### status.md template

```markdown
# {Feature} — Status

## Current Phase: {N}
## Overall: {🟢 On Track / 🟡 At Risk / 🔴 Blocked}

| Phase | Status | Gate |
|-------|--------|------|

## Decisions
- {link to ADRs}

## Blockers
- {current blockers}

## Log
- **{date}** — Plan created
```

## Rules

- Scope confirmation BEFORE planning
- Architecture approval BEFORE task breakdown
- Every phase has a gate
- Estimates use three-point ranges
- Save to LOCAL project directory first, memory second
- Read product context dynamically from PRODUCTS.md — never hardcode product names
- Create ADRs (via /project:adr) for significant tech decisions
