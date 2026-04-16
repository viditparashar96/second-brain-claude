---
name: eng-incident-response
description: "Multi-phase incident response — detection, investigation, mitigation, resolution, and postmortem with hypothesis-driven diagnostics."
argument-hint: "[new|escalate|update|postmortem] [incident-title] [--severity P0|P1|P2|P3]"
triggers:
  - "incident"
  - "outage"
  - "system down"
  - "production issue"
  - "site is down"
  - "service degraded"
  - "postmortem"
  - "P0"
  - "P1"
  - "SEV1"
  - "on-call"
---

# Incident Response Commander

5-phase incident management: Detect → Investigate → Mitigate → Resolve → Postmortem. Blameless, hypothesis-driven, product-aware.

## Workflow

### Phase 1: DETECT — Classify (< 2 min)
1. Parse: what's happening, when, who reported
2. Read PRODUCTS.md — **Ultrathink** to match incident to product, identify tech stack and dependencies dynamically
3. Classify severity:
   - **P0** Critical: revenue-impacting, full outage, data loss → Immediate
   - **P1** High: major feature broken → < 30 min
   - **P2** Medium: workaround exists → < 4 hours
   - **P3** Low: minor → next sprint
4. **🚫 GATE — Severity confirmed**
5. Create incident record at `docs/incidents/{INC-YYYYMMDD-NNN}.md`

### Phase 2: INVESTIGATE — Hypothesis-Driven
1. **Ultrathink** — Generate 3-7 hypotheses ranked by probability, using the product's tech stack for targeted diagnostics
2. Search memory for similar past incidents
3. Test hypotheses most-likely-first:
   - Present diagnostic → wait for output → **Midthink** → update evidence board
4. Converge when one hypothesis >90% confidence
5. **🚫 GATE — Root cause confirmed**

### Phase 3: MITIGATE — Stop the Bleeding
1. Generate mitigation options (quick fix vs proper fix, with risk/reversibility)
2. **🚫 GATE — Mitigation approach approved**
3. Guide through execution
4. Verify service restored
5. Draft stakeholder notification → **🚫 GATE — Comms approved before sending**

### Phase 4: RESOLVE — Permanent Fix
1. Design permanent fix
2. Create action items with owners and dates
3. Update incident status

### Phase 5: POSTMORTEM (P0/P1, within 48h)
1. Generate postmortem at `docs/postmortems/{id}-postmortem.md`
2. Include: summary, timeline, 5 Whys, action items, lessons
3. **🚫 GATE — Postmortem reviewed before finalizing**
4. Log key learnings to memory

## Output Templates

### Incident Record
```markdown
---
incident_id: "{id}"
severity: "{P-level}"
status: "investigating"
product: "{product}"
started_at: "{timestamp}"
---
# {id}: {title}
## Timeline
## Impact
## Root Cause
## Actions
```

### Postmortem
```markdown
# Postmortem: {id}
## Summary
## Timeline
## Root Cause (5 Whys)
## What Went Well / Wrong
## Action Items
| Action | Owner | Due | Status |
```

## Rules
- Severity FIRST, diagnostics second
- External comms require explicit approval
- Blameless — systems, not individuals
- Minimum 3 hypotheses
- All artifacts saved to **local project `docs/`**
- Log summary to memory — one line
- Product tech stack read dynamically from PRODUCTS.md

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
