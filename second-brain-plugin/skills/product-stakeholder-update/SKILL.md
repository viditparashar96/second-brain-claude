---
name: product-stakeholder-update
description: Generate weekly or monthly status updates by synthesizing vault and integration data
argument-hint: "[period: this-week|last-week|this-month] [audience: team|leadership|client] [format: email|brief|report]"
triggers:
  - "status update"
  - "weekly update"
  - "monthly update"
  - "stakeholder update"
  - "progress report"
  - "team update"
  - "leadership brief"
  - "client update"
---

# Stakeholder Update

Generate comprehensive status updates for different audiences by synthesizing daily logs, completed tasks, merged PRs, meeting decisions, and OKR progress. Adapts tone and focus to audience (team updates are casual, leadership updates are metrics-focused, client updates are polished).

## When to Trigger

- Weekly standup or status round-up (this-week option)
- Monthly business review or stakeholder report
- Executive update for leadership/board
- Client progress report on engagement or project
- End-of-period summary before new cycle
- Quick status check for specific team or stakeholder group

## Workflow

1. **Parse period, audience, and format** — Extract from user input:
   - Period: this-week, last-week, this-month, last-month, custom-range
   - Audience: team (internal, casual), leadership (metrics-focused), client (polished, external)
   - Format: email (draft in Gmail), brief (1-pager), report (full document)

2. **Pull product and org context** — From PRODUCTS.md (already in session context), identify relevant products for the update period. From ORG.md (already in session context), pull strategic goals to frame progress in terms of company priorities.

3. **Fetch period activity** — Collect data from multiple sources:

   **Daily Logs**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<period>" --path "daily" --top-k 20
   ```
   Extract: decisions made, milestones, team updates, metrics mentioned

   **Completed Asana Tasks**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana search "" --status "Complete" --modified-after "<period-start>"
   ```
   List: completed work, deliverables shipped, projects advanced

   **Merged PRs** (if GitHub connected):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" github search "is:merged merged:><period-start>" --q ""
   ```
   Extract: shipped features, bug fixes, infrastructure improvements

   **Meeting Decisions**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "decision made" --path "meetings" --top-k 10
   ```
   Capture: key decisions, commitments, strategy shifts

   **OKR Progress**:
   ```bash
   cat ~/.second-brain/vault/product/okrs/<current-period>.md
   ```
   Extract: progress on key objectives, at-risk items

4. **Synthesize into structured update** with sections tailored to audience:

   **All Audiences**:
   - **Highlights** — Top 3-5 wins, shipped features, metrics improvements
   - **Progress on Goals** — Status against OKRs, roadmap items
   - **Blockers & Risks** — What's preventing progress, mitigation plans
   - **Upcoming Priorities** — What's next, upcoming deadlines

   **Leadership Audience (add)**:
   - **Key Metrics** — Progress on business metrics, KPIs
   - **Decisions Made** — Major choices, strategy shifts
   - **Budget/Resource Impact** — Staffing, cost implications

   **Client Audience (add)**:
   - **Deliverables** — What was shipped, when, value delivered
   - **Timeline** — On-track or adjusted scope/schedule
   - **Next Steps** — What's coming, when to expect, dependencies

5. **Adapt tone to audience**:
   - Team updates: casual, internal jargon okay, celebratory
   - Leadership updates: formal, metrics-focused, strategic context
   - Client updates: professional, value-focused, clear language

6. **For email format** — Create Gmail draft:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail draft-update "[audience] Update: [period]" "<content>"
   ```
   User can review and send, or edit before sending

7. **For brief/report format** — Save to vault:
   ```bash
   ~/.second-brain/vault/product/updates/YYYY-MM-DD-<audience>-update.md
   ```
   
8. **Add cross-references** — Link to related projects, decisions, OKRs using [[wiki-links]]

9. **Log to daily log**:
   ```bash
   - **HH:MM** — [UPDATE] Generated <period> <audience> update — <highlight-count> wins, <blocker-count> blockers
   ```

## Rules

- **Team updates** — Celebrate wins, flag blockers, energize the group
- **Leadership updates** — Focus on metrics, business impact, strategic decisions, risks that need visibility
- **Client updates** — Emphasize delivered value, progress on their goals, clear next steps and timeline
- Keep updates concise: 1 page (brief), 2-3 pages (report), 1-2 paragraphs (email)
- Only highlight metrics that matter to the audience (team cares about velocity, leaders care about business KPIs)
- Blockers should include mitigation plan, not just problem statement
- Always date updates and note the period covered
- Link back to source vault files for transparency and traceability
- Stakeholder updates should reference ORG.md strategic goals and relevant PRODUCTS.md entries to tie progress to company priorities.

## Templates

### Team Update Template

```markdown
# Team Update: [Period]

**Date**: YYYY-MM-DD  
**Period**: [e.g., Week of Apr 7-11]

## Highlights

- [Major win shipped, feature launched, metric improved]
- [Team accomplishment, great collaboration example]
- [Risk mitigated, blocker unblocked]

## Progress on Goals

- [Objective 1]: [progress %, on-track/at-risk]
- [Objective 2]: [progress %, on-track/at-risk]

## What We Shipped

- [Feature or deliverable]
- [Bug fix or improvement]

## Blockers & Support Needed

- [Blocker]: [mitigation plan]
- [Blocker]: [who needs to help]

## Next Week's Focus

- [Priority 1]
- [Priority 2]

---
[[product/okrs]] | [[projects]]
```

### Leadership Update Template

```markdown
# Leadership Update: [Period]

**Date**: YYYY-MM-DD  
**Period**: [e.g., April 1-30]

## Executive Summary

[2-3 sentences: major wins, key metrics, business impact]

## Key Metrics

- [Metric Name]: [value] (target: [value], on-track: yes/no)
- [Metric Name]: [value] (target: [value], on-track: yes/no)

## Major Deliverables

- [Shipped feature] — impact: [business value]
- [Shipped feature] — impact: [business value]

## Strategic Decisions Made

- [Decision]: [rationale, impact]
- [Decision]: [rationale, impact]

## Risks & Mitigation

- [Risk]: [likelihood/impact], Mitigation: [action]
- [Risk]: [likelihood/impact], Mitigation: [action]

## Resource Needs

- [Staffing, budget, or other resource request]

## Next Period Priorities

- [Objective 1]
- [Objective 2]

---
[[product/okrs]] | [[projects]]
```

### Client Update Template

```markdown
# Project Update: [Project Name]

**Date**: YYYY-MM-DD  
**Period**: [e.g., Week of Apr 7-11]  
**Prepared for**: [Client Name]

## Summary

[1-2 sentences on overall progress toward client goals]

## Deliverables This Period

- [Feature/milestone delivered] — Date: [date], Status: [complete/in-progress]
- [Feature/milestone delivered] — Date: [date], Status: [complete/in-progress]

## Progress on Goals

- [Client Goal 1]: [progress %, on-track]
- [Client Goal 2]: [progress %, on-track]

## Timeline Status

- **Original Timeline**: [dates]
- **Current Status**: [on-track/adjusted], Reason: [if adjusted]
- **Next Milestone**: [description, expected date]

## Next Steps

- [What we're delivering next]
- [Dependencies from client, if any]
- [Timeline for next phase]

## Questions or Decisions Needed

- [Decision item with timeline]

---
[[projects/<project-slug>]]
```

## Email Format Example

Subject: [Audience] Update — [Period]

Hello [recipient],

Here's this week's progress:

**Highlights**
- [Win 1]
- [Win 2]

**Progress on Goals**
[1-2 sentences on key objectives, metrics]

**Blockers**
[If any, with mitigation plan]

**Next Steps**
[What's coming next]

Best,
[Your name]
