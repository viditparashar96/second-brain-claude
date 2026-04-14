---
name: eng-plan
description: "Implementation planner — breaks down features into phased milestones with architecture, risks, three-point estimates, and gate-controlled execution."
argument-hint: "[feature-description] [--product name] [--timeline X weeks]"
triggers:
  - "plan"
  - "implementation plan"
  - "break down"
  - "how should we build"
  - "project plan"
  - "feature plan"
  - "roadmap"
  - "estimate"
  - "how long will"
  - "scope this"
  - "plan this feature"
  - "execution plan"
---

# Implementation Planner

Structured planning workflow: scope → architect → phase breakdown → track. Produces local documentation artifacts for developer review.

## Workflow

### Phase 1: SCOPE
1. Read project docs (`docs/`, `README.md`, `ARCHITECTURE.md`)
2. Read org context (`~/.second-brain/vault/PRODUCTS.md`, `ORG.md`) — extract relevant product tech stack dynamically
3. Search memory for related work
4. Define: problem statement, success criteria, scope IN/OUT, constraints
5. **🚫 GATE — Scope confirmed before planning**

### Phase 2: ARCHITECT
1. **Ultrathink** — Explore solution space using the product's actual tech stack
2. Propose architecture (ASCII diagram)
3. Identify risks (probability × impact, mitigations)
4. Map dependencies
5. **🚫 GATE — Architecture approved**

### Phase 3: PHASE BREAKDOWN
1. Break into phases (max 1 week each), starting with Phase 0 (Spike) for unknowns
2. Each phase: goal, tasks, deliverable, gate criteria
3. Three-point estimates (optimistic / expected / pessimistic)
4. Suggest ownership
5. **🚫 GATE — Plan approved**

### Phase 4: DOCUMENT (LOCAL FIRST)
1. Save `docs/plans/{feature-slug}-plan.md` in the local project
2. Save `docs/plans/{feature-slug}-status.md` as tracker
3. Create tasks for each phase
4. Log one-line summary to memory via `log_note`

## Output Templates

### plan.md
```markdown
---
title: "{feature}"
date: "{date}"
status: "approved"
product: "{product}"
---
# {Feature} — Implementation Plan
## Problem Statement
## Success Criteria
## Architecture
## Risks
| Risk | Probability | Impact | Mitigation |
## Dependencies
| Dependency | Owner | Status | Blocker? |
## Phases
### Phase 0: Spike
**Goal:** | **Gate:** | **Tasks:** [ ]
## Estimates
| Phase | Optimistic | Expected | Pessimistic |
```

### status.md
```markdown
# {Feature} — Status
## Current Phase: | Overall: {🟢🟡🔴}
| Phase | Status | Gate |
## Blockers
## Log
```

## Rules
- Scope → Architecture → Phases (never skip order)
- Every phase has a gate with measurable criteria
- Three-point estimates always
- Save to **local project `docs/`** — developer reviews the plan in the repo
- Log summary to memory — one line, not the full plan
- Product context read dynamically from PRODUCTS.md — never hardcode product names or tech stacks
