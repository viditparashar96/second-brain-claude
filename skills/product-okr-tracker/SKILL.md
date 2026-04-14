---
name: product-okr-tracker
description: Define, track, and report on OKRs (Objectives and Key Results)
argument-hint: "[command: set|update|review|report] [period] [details]"
triggers:
  - "set OKR"
  - "OKR"
  - "track objectives"
  - "key results"
  - "okr update"
  - "okr review"
  - "okr report"
  - "quarterly goals"
---

# OKR Tracker

Define, track, and report on OKRs (Objectives and Key Results). Maintains a living document of organizational objectives with measurable key results, tracks progress against evidence from Asana and daily logs, and generates stakeholder-ready summaries.

## When to Trigger

- User wants to set new OKRs for a period (quarter, half, year)
- Need to update progress on existing OKRs
- Reviewing OKR status — which are on-track, at-risk, behind?
- Generating OKR report for stakeholders, board, or team
- Weekly/monthly check-in on progress toward goals
- Identifying at-risk OKRs that need corrective action

## Workflow

1. **Parse command and period** — Extract: set|update|review|report, period (e.g., 2026-Q2), any provided OKR details

2. **Load or create OKR file** — Run:
   ```bash
   cat ~/.second-brain/vault/product/okrs/<period-slug>.md
   ```
   If not found, create new file with current OKRs or template

3. **For SET command** — Define new OKRs:
   - Parse user input: objective (1-2 sentences), key results (3-5 measurable outcomes with targets)
   - Extract owner from user context or prompt for assignment
   - Store in vault file with initial progress = 0%, status = "Not Started"
   - Log to daily log

4. **For UPDATE command** — Log progress:
   - Fetch related Asana completed tasks:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana search "<OKR-name>" --status "Complete"
     ```
   - Pull merged PRs if GitHub connected:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" github search "is:merged" --q "<OKR-name>"
     ```
   - Search daily log for recent progress mentions:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<OKR-name> progress completed" --top-k 3
     ```
   - Calculate current progress % against each key result
   - Determine status: on-track (>80% expected progress), at-risk (50-80%), behind (<50%)
   - Update vault file with evidence links and new progress %
   - Flag at-risk/behind OKRs for attention
   - Log to daily log

5. **For REVIEW command** — Status snapshot:
   - Load OKR file, compile status of all objectives
   - Highlight: on-track OKRs, at-risk OKRs requiring action, behind OKRs needing escalation
   - Return structured summary to user with talking points

6. **For REPORT command** — Generate stakeholder summary:
   - Load OKR file, compile all objectives and current progress
   - Generate sections:
     - **Overview** — Period, number of objectives, overall health
     - **On-Track OKRs** — List with progress %, why confident
     - **At-Risk OKRs** — List with progress %, blockers, mitigation plan
     - **Behind OKRs** — List with progress %, root cause, corrective action
     - **Key Wins This Period** — Major milestones achieved
     - **Priorities for Next Period** — What's coming next
   - Format as polished Markdown document
   - Save to:
     ```bash
     ~/.second-brain/vault/product/okrs/YYYY-MM-DD-<period>-report.md
     ```
   - Offer to create Gmail draft for email send

7. **Log all OKR actions** to daily log:
   ```bash
   - **HH:MM** — [OKR] <command>: <period> — <summary>
   ```

## Rules

- Each objective should have 3-5 key results (not more)
- Key results must be measurable — vague targets don't work
- Progress % is calculated from: completed/in-progress tasks, completed milestones, evidence from daily logs
- At-risk or behind status requires owner to note blockers and mitigation plan
- OKRs typically set once per quarter, reviewed weekly, reported monthly
- Always link OKRs to related projects, PRDs, and initiatives using [[wiki-links]]
- At-risk and behind OKRs surface in status reports and require escalation

## Templates

Use this structure for OKR file:

```markdown
# OKRs: [Period] (e.g., 2026-Q2)

**Period**: YYYY-MM-DD to YYYY-MM-DD  
**Last Updated**: YYYY-MM-DD  
**Overall Health**: [On-Track | At-Risk | Mixed]

## Objective 1: [1-2 sentence objective]

**Owner**: [name]  
**Status**: [Not Started | On-Track | At-Risk | Behind | Complete]

### Key Results

1. [Measurable outcome] — Target: [value]
   - Current: [current value] ([progress %])
   - Evidence: [[related-project]] — [task completion, metric source]

2. [Measurable outcome] — Target: [value]
   - Current: [current value] ([progress %])
   - Evidence: [[related-project]] — [task completion, metric source]

3. [Measurable outcome] — Target: [value]
   - Current: [current value] ([progress %])
   - Evidence: [[related-project]] — [task completion, metric source]

**Blockers** (if at-risk/behind): [what's preventing progress]  
**Mitigation**: [action to get back on-track]

## Objective 2: [...]

---
[[product/prds]] | [[projects]]
```

## Report Template

```markdown
# OKR Report: [Period]

**Date**: YYYY-MM-DD  
**Period**: [e.g., 2026-Q2]  
**Overall Health**: [summary % on-track]

## Overview

[1-2 paragraphs on overall progress, major wins, key blockers]

## On-Track OKRs

- **[Objective Name]** (Owner: [name]) — [progress %]
  - [Key result 1]: [current] / [target]
  - [Key result 2]: [current] / [target]
  - Why confident: [brief explanation]

## At-Risk OKRs

- **[Objective Name]** (Owner: [name]) — [progress %]
  - Blocker: [what's preventing progress]
  - Mitigation: [action to recover]

## Behind OKRs

- **[Objective Name]** (Owner: [name]) — [progress %]
  - Root cause: [why we're behind]
  - Corrective action: [what we're doing to recover]

## Key Wins This Period

- [Major milestone achieved]
- [Significant progress]

## Priorities for Next Period

- [Objective 1 for next period]
- [Objective 2 for next period]

---
[[product/okrs/<period>]]
```
