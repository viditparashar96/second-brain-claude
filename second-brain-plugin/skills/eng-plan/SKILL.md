---
name: eng-plan
description: "Implementation planner — creates a task folder with plan, status, decisions, and implementation notes. Selective expert analysis, phased milestones, and gate-controlled execution."
argument-hint: "[task-description] [--product name] [--timeline X weeks]"
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

Structured planning workflow: scope → architect → phase breakdown → document. Produces a **task folder** with 4 documentation artifacts for developer review.

## Output Structure

Each planned task creates:

```
docs/plans/{task-name}/
├── plan.md                  # Goal, architecture, phases, steps, files to modify
├── status.md                # Progress tracking with phase gates
├── decisions.md             # Decision log with context & rationale
├── implementation-notes.md  # Full technical deep-dive, code patterns, references
```

## Workflow

### Step 1: GET TASK DESCRIPTION

Check if task description was provided via arguments.

**If empty:** Ask: "What feature or task do you want to plan? Describe what needs to be built."

**If provided:** Use directly. Example: `/eng-plan add real-time GPS tracking to School Cab`

### Step 2: GENERATE TASK NAME

Auto-generate a kebab-case folder name from the description.

**Rules:**
- Lowercase, hyphens for spaces, no special chars
- Concise but descriptive — extract key action + subject
- Check if `docs/plans/{task-name}/` exists; if so, append `-2`, `-3`, etc.

**Examples:**
- "add real-time GPS tracking" → `add-gps-tracking`
- "implement voice agent pipeline" → `implement-voice-pipeline`
- "build school cab MVP" → `build-school-cab-mvp`

### Step 3: SCOPE (Gate 1)

1. Read project docs (`docs/`, `README.md`, `ARCHITECTURE.md`) if they exist
2. Read org context (`PRODUCTS.md`, `ORG.md` in vault) — extract relevant product tech stack dynamically
3. Search memory for related work
4. Define: problem statement, success criteria, scope IN/OUT, constraints

**🚫 GATE — Scope confirmed before planning. Present scope to user and wait for approval.**

### Step 4: SELECTIVE EXPERT ANALYSIS

**IMPORTANT**: Use judgment to determine which analysis areas are relevant. Do NOT analyze everything — only what adds value for this specific task.

#### Decision Matrix

Analyze the task and determine which areas to investigate:

**Frontend/UI Tasks:**
- ✅ Component architecture, state management, styling
- ✅ Consider: API integration if fetching data
- ❌ Skip: Infrastructure, database, deployment

**API/Backend Tasks:**
- ✅ Route design, middleware, error handling
- ✅ Consider: Database (if queries needed), auth (if protected)
- ❌ Skip: UI components, styling

**Database Tasks:**
- ✅ Schema design, queries, migrations, indexing
- ✅ Consider: API layer (for integration)
- ❌ Skip: UI, styling

**Infrastructure/DevOps Tasks:**
- ✅ Architecture, deployment, scaling, monitoring
- ✅ Consider: Security, cost analysis
- ❌ Skip: UI, component patterns

**Full-Stack Features:**
- Route based on feature components — consult all relevant areas
- Example: "Add dashboard" → UI + API + Database + Auth

**Voice/AI Tasks:**
- ✅ Pipeline architecture, model selection, latency
- ✅ Consider: Telephony, STT/TTS, transport layer
- ❌ Skip: Unrelated UI, unrelated database

**Mobile App Tasks:**
- ✅ App architecture, navigation, platform APIs
- ✅ Consider: Backend API, real-time features
- ❌ Skip: Unrelated web UI patterns

#### How to Gather Expert Analysis

For each relevant area, use **subagents** (Agent tool) to research in parallel:

1. **Codebase analysis** — Read existing code patterns, identify files to modify
2. **Documentation research** — Use context7 MCP or WebSearch for framework/library docs
3. **Product context** — Pull tech stack and constraints from PRODUCTS.md
4. **Memory search** — Check vault for related past work, decisions, lessons learned

**Key Principle**: Only investigate areas that add value. Quality over quantity.

### Step 5: ARCHITECT (Gate 2)

1. **Ultrathink** — Explore solution space using the product's actual tech stack
2. Synthesize expert analysis into a recommended approach
3. Propose architecture (ASCII diagram if helpful)
4. Identify risks (probability x impact, mitigations)
5. Map dependencies (owner, status, blocker?)

**🚫 GATE — Architecture approved. Present to user and wait for approval.**

### Step 6: PHASE BREAKDOWN (Gate 3)

1. Break into phases (max 1 week each), starting with Phase 0 (Spike) for unknowns
2. Each phase: goal, tasks (checkboxes), deliverable, gate criteria
3. Three-point estimates (optimistic / expected / pessimistic)
4. Suggest ownership
5. List files to modify per phase

**🚫 GATE — Plan approved. Present to user and wait for approval.**

### Step 7: CREATE TASK DOCUMENTATION

Create the task folder and all 4 files:

```bash
mkdir -p docs/plans/{task-name}
```

#### plan.md

```markdown
---
title: "{task-name}"
date: "{date}"
status: "approved"
product: "{product}"
---

# {Task Name} — Implementation Plan

## Goal
{Task description from user}

## Problem Statement
{Why this needs to be built, what problem it solves}

## Success Criteria
- [ ] {Measurable criterion 1}
- [ ] {Measurable criterion 2}

## Scope
**IN:** {What's included}
**OUT:** {What's explicitly excluded}

## Expert Analysis Summary

### {Area 1}
{Summary of key findings}

### {Area 2} (if consulted)
{Summary of key findings}

## Architecture
{ASCII diagram or description of the solution architecture}

## Recommended Approach
{Implementation strategy synthesized from expert analyses}

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| {risk} | {H/M/L} | {H/M/L} | {mitigation} |

## Dependencies
| Dependency | Owner | Status | Blocker? |
|-----------|-------|--------|----------|
| {dep} | {owner} | {status} | {Y/N} |

## Phases

### Phase 0: Spike
**Goal:** {Resolve unknowns}
**Gate:** {Criteria to proceed}
**Tasks:**
- [ ] {task}

### Phase 1: {Name}
**Goal:** {phase goal}
**Gate:** {Criteria to proceed}
**Estimate:** {optimistic} / {expected} / {pessimistic}
**Tasks:**
- [ ] {task}

**Files to Modify:**
- `path/to/file` — {expected changes}

## Anti-Patterns to Avoid
- {anti-pattern}: {why}

## Estimates Summary
| Phase | Optimistic | Expected | Pessimistic |
|-------|-----------|----------|-------------|
| Phase 0 | {x} | {x} | {x} |
| Phase 1 | {x} | {x} | {x} |
| **Total** | **{x}** | **{x}** | **{x}** |

## Acceptance Criteria
- [ ] Feature works as described
- [ ] Tests pass
- [ ] No regressions
- [ ] {task-specific criteria}

## References
{Documentation links from expert analyses}
```

#### status.md

```markdown
# {Task Name} — Status

**Current Phase:** Planning
**Overall:** {status-emoji}
**Last Updated:** {timestamp}

## Progress

| Phase | Status | Gate |
|-------|--------|------|
| Phase 0: Spike | {status} | {gate criteria} |
| Phase 1: {name} | Not Started | {gate criteria} |

## Expert Analysis

{List only the areas that were actually consulted}
- {area}: {1-2 sentence summary}

## Next Steps
- [ ] Review plan.md and refine approach
- [ ] Begin Phase 0 (Spike)
- [ ] Update status as you progress

## Blockers
None currently.

## Log
- {date} — Task planning initiated via /eng-plan
```

#### decisions.md

```markdown
# {Task Name} — Decisions

## Decision Log

### {date} — Initial Planning Approach

**Context:** Task planning initiated. {Brief context on why this task exists.}

**Options Considered:**
1. {Option A} — {tradeoffs}
2. {Option B} — {tradeoffs}

**Decision:** {What was decided}

**Rationale:**
- {Reason 1}
- {Reason 2}

---

## Pending Decisions

{List decisions that need to be made during implementation}

1. **{Decision topic}**
   - Options: {A, B, C}
   - Considerations: {Tradeoffs}
   - Status: Pending
   - Decide by: {phase or date}
```

#### implementation-notes.md

```markdown
# {Task Name} — Implementation Notes

## Planning Phase

### {Area 1} Analysis (Full)

{Complete analysis from expert/subagent research}

---

### {Area 2} Analysis (Full)

{Complete analysis from expert/subagent research}

---

## Technical Considerations

{Key technical points from analyses}

## Code Patterns to Use

{Specific patterns identified — with code examples where helpful}

## Constraints

{Product-specific constraints from PRODUCTS.md, tech stack limitations}

## Resources

{Documentation links, related PRs, vault references}
```

### Step 8: SUMMARY

After creating all documentation, present:

```markdown
## Task Planning Complete: {task-name}

**Created:** `docs/plans/{task-name}/`

**Expert Analysis:**
- {area}: {1-2 sentence summary}

**Recommended Approach:**
{2-4 sentences summarizing the strategy}

**Key Files:**
- {file list with expected changes}

**Estimates:** {optimistic} / {expected} / {pessimistic}

**Next Steps:**
1. Review `docs/plans/{task-name}/plan.md`
2. Begin Phase 0 (Spike)
3. Update `status.md` as you progress
```

Log one-line summary to daily notes.

## Rules

- Scope → Architecture → Phases → Document (never skip order)
- Every phase has a gate with measurable criteria
- Three-point estimates always
- **Selective expert analysis** — only investigate relevant areas, not everything
- Use subagents for parallel research where possible
- Save to **local project `docs/plans/`** — developer reviews in the repo
- Log summary to memory — one line, not the full plan
- Product context read dynamically from PRODUCTS.md — never hardcode
- If task folder exists, warn and ask before overwriting

## Edge Cases

- **Vague description:** Ask for specifics before proceeding
- **Folder exists:** Warn user, ask to overwrite or rename
- **No product context:** Proceed without PRODUCTS.md, note the gap
- **Cross-product task:** Pull context from all relevant products
