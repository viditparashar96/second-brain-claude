---
name: eng-sprint-retro
description: "Facilitated sprint retrospective — collects feedback, identifies cross-sprint patterns, generates tracked action items with owners."
argument-hint: "[sprint-name|number] [--team name] [--format standard|4Ls|starfish|sailboat]"
triggers:
  - "sprint retro"
  - "retrospective"
  - "retro"
  - "sprint review"
  - "what went well"
  - "what went wrong"
  - "lessons learned"
  - "sprint wrap"
  - "end of sprint"
---

# Sprint Retrospective Facilitator

Collect feedback → cluster themes → detect cross-sprint patterns → generate tracked actions.

## Workflow

### Phase 1: SETUP
1. Determine: sprint name, team/product, duration, goals, format
2. Read PRODUCTS.md for product context (dynamically)
3. Check `docs/retros/` for past retros — present carry-forward action items
4. Search daily logs and memory for sprint events
5. **🚫 GATE — Carry-forward items confirmed**

### Phase 2: COLLECT
Gather feedback one category at a time:

**Standard:** 🟢 Went Well → 🔴 Didn't Go Well → 🔵 Change
**4Ls:** Liked → Learned → Lacked → Longed For
**Starfish:** Keep → More Of → Less Of → Start → Stop
**Sailboat:** Wind (propelling) → Anchor (slowing) → Rocks (risks) → Island (goal)

Prompt with sprint context (releases, incidents, blockers from logs).

### Phase 3: ANALYZE
1. **Ultrathink** — Cluster feedback into themes
2. Search memory for recurring themes across past retros
3. If theme appears 3+ sprints → flag RECURRING with trend (improving/worsening/stable)
4. Worsening recurring themes → recommend escalation

### Phase 4: ACTIONS
1. Propose 1-3 actions per theme, each with OWNER and DUE DATE
2. **🚫 GATE — Actions approved with owners assigned**
3. Create tasks via `create_task` MCP tool

### Phase 5: DOCUMENT (LOCAL FIRST)
1. Save `docs/retros/{sprint-id}-retro.md` in local project:
   ```markdown
   ---
   sprint: "{name}"
   date: "{date}"
   team: "{team}"
   ---
   # Sprint {N} Retrospective
   ## What Went Well 🟢
   ## What Didn't Go Well 🔴
   ## Themes
   ## Action Items
   | Action | Owner | Due | Status |
   ## Carried Forward
   ```
2. Log summary to memory via `log_note`

## Rules
- Blameless — systems, not people
- Actions without owners are not real actions
- Recurring themes (3+) trigger escalation
- Always review past retro actions first
- Save locally first, memory second
