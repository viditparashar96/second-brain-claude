---
name: sales-pipeline-review
description: Summarize deal pipeline status from Asana and vault — stages, values, stale deals, deadlines
argument-hint: "[optional-filters]"
triggers:
  - "pipeline review"
  - "deal status"
  - "how many deals"
  - "pipeline snapshot"
  - "what's in the pipeline"
  - "stale deals"
  - "action items"
---

# Pipeline Review

Generate a comprehensive pipeline snapshot from Asana and vault data. Pulls all active deals, cross-references client context, checks email recency, and highlights stale deals and upcoming deadlines. Helps identify action items and at-risk opportunities.

## When to Trigger

- User asks for a pipeline review or summary
- Weekly/monthly standup to understand deal status
- Heartbeat detects end-of-week/month and prompts pipeline review
- User asks "what's in our pipeline" or "how many deals are we working"
- Need to identify which deals are stalling

## Workflow

1. **Fetch active deals from Asana** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana search "" --section "Sales" --status "Not Started,In Progress" --max 50
   ```
   Get all active sales tasks/deals

2. **Parse deal info** from Asana tasks:
   - Deal name / client name
   - Current stage (custom field if available)
   - Estimated value (if tracked in Asana)
   - Due date / target close date
   - Task owner
   - Last updated date

3. **For each deal, load client context** — Run:
   ```bash
   cat ~/.second-brain/vault/clients/<client-slug>.md
   ```
   Extract: company overview, relationship stage, deal history

4. **Check email recency** for each deal — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<client-email>" --max 1
   ```
   Get date of last contact with client (how fresh is the relationship?)

5. **Identify stale deals** — Flag any deals where:
   - Last email from client > 7 days ago
   - Asana task not updated > 7 days
   - No clear timeline or next step

6. **Identify at-risk deals** — Flag any deals where:
   - Due date is within 3 days (urgent action needed)
   - Multiple stale tasks in same deal
   - Client communication gap

7. **Generate pipeline summary** with sections:
   - **Pipeline Overview** — Total deals, total value, average deal size
   - **Deals by Stage** — Breakdown of deals in each stage
   - **Upcoming Deadlines** — Next 7 days (proposals due, decision dates)
   - **Stale Deals** — Deals needing re-engagement (no activity >7 days)
   - **At-Risk Deals** — Deals with deadlines + communication gaps
   - **Action Items** — What needs to happen this week (proposals, calls, follow-ups)

8. **Save pipeline snapshot** to:
   ```bash
   ~/.second-brain/vault/sales/pipeline/YYYY-MM-DD-pipeline.md
   ```

9. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] Pipeline review: <total-deals> deals, $<total-value>, <stale-count> stale, <action-count> actions
   ```

## Rules

- **Deals by stage**: Use Asana custom field or infer from task name/description (lead, qualify, propose, negotiate, close)
- **Email recency**: If multiple emails from same client, use the most recent one
- **Stale threshold**: >7 days with no update or email = stale
- **At-risk threshold**: Due date within 3 days + communication gap
- **Value tracking**: If not available in Asana, search vault client notes or mark as "TBD"
- **Cross-reference**: Link to client vault files and deal notes using [[wiki-links]]
- **Weekly snapshots**: Save dated snapshots to track trends over time
- **Action items**: List specific next steps (call, email, proposal, decision) with target date

## Templates

Use this structure for pipeline snapshot file:

```markdown
# Sales Pipeline Review

**Date**: [YYYY-MM-DD]
**Prepared by**: [name]
**Review period**: [week of / month of]

---

## Pipeline Overview

- **Total Active Deals**: [count]
- **Total Pipeline Value**: $[value]
- **Average Deal Size**: $[value]
- **Win Rate (last 30 days)**: [X%]
- **Deals Stalled**: [count] (>7 days no activity)
- **Deals At Risk**: [count] (deadline + communication gap)

---

## Deals by Stage

### Leads (New Prospects)
| Client | Contact | Value | Last Contact | Status |
|--------|---------|-------|--------------|--------|
| [name] | [person] | $[est] | [date] | [notes] |

**Count**: [X] deals | **Total Value**: $[value]

### Qualify (Discovery & Fit)
| Client | Contact | Value | Next Step | Due |
|--------|---------|-------|-----------|-----|
| [name] | [person] | $[est] | [next action] | [date] |

**Count**: [X] deals | **Total Value**: $[value]

### Propose (Proposal Sent)
| Client | Contact | Value | Proposal Date | Expected Decision |
|--------|---------|-------|---------------|-------------------|
| [name] | [person] | $[est] | [date] | [date] |

**Count**: [X] deals | **Total Value**: $[value]

### Negotiate (In Discussion)
| Client | Contact | Value | Key Blocker | Timeline |
|--------|---------|-------|-------------|----------|
| [name] | [person] | $[est] | [blocker] | [date] |

**Count**: [X] deals | **Total Value**: $[value]

### Close (Final Stage)
| Client | Contact | Value | Expected Close | Confidence |
|--------|---------|-------|-----------------|------------|
| [name] | [person] | $[est] | [date] | [high/med/low] |

**Count**: [X] deals | **Total Value**: $[value]

---

## Upcoming Deadlines (Next 7 Days)

| Date | Action | Client | Owner | Status |
|------|--------|--------|-------|--------|
| [date] | [action] | [client] | [owner] | [on-track/at-risk] |
| [date] | [action] | [client] | [owner] | [on-track/at-risk] |

---

## Stale Deals (>7 days no activity)

| Client | Stage | Last Contact | Last Update | Action Needed |
|--------|-------|--------------|-------------|---------------|
| [name] | [stage] | [date] | [date] | [re-engage / check-in / proposal needed] |
| [name] | [stage] | [date] | [date] | [re-engage / check-in / proposal needed] |

**Total Stale**: [count] deals worth $[value] — **PRIORITY**: Re-engage these this week.

---

## At-Risk Deals (Deadline + Communication Gap)

| Client | Stage | Due | Days Until Due | Issue | Risk Level |
|--------|-------|-----|----------------|-------|------------|
| [name] | [stage] | [date] | [X] | [issue] | HIGH/MED |

**Action**: [specific intervention needed for each]

---

## Weekly Action Items

- [ ] **Re-engage stale deals** — Call or email [clients] by [day]
- [ ] **Send proposals** — [client] needs proposal by [date]
- [ ] **Follow-up calls** — Check in with [clients] on [stage]
- [ ] **Close conversations** — Final push on [client] decision by [date]
- [ ] **Update Asana** — Refresh all task statuses and dates

---

## Notes & Observations

[Optional: Any trends noticed? Seasonal patterns? Market conditions affecting deals?]

---

## Previous Reviews

- [[sales/pipeline/YYYY-MM-DD-pipeline]]
- [[sales/pipeline/YYYY-MM-DD-pipeline]]

---

*Generated by Pipeline Review skill. Last updated: [timestamp]*
```

## Metrics to Track

Use this optional section in pipeline files to track over time:

```markdown
## Pipeline Metrics

| Metric | Last Review | This Review | Change |
|--------|------------|------------|--------|
| Total Active Deals | [X] | [X] | [+/-X] |
| Total Value | $[X] | $[X] | [+/-$X] |
| Average Deal Size | $[X] | $[X] | [+/-$X] |
| Deals in Proposal | [X] | [X] | [+/-X] |
| Deals in Negotiation | [X] | [X] | [+/-X] |
| Stale Deal Count | [X] | [X] | [+/-X] |
| Deals Closed (YTD) | [X] | [X] | [+X] |
| Average Close Time | [X] days | [X] days | [+/-X] |
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
