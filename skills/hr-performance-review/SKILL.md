---
name: hr-performance-review
description: Prep tool that gathers context for writing performance reviews — searches vault for meetings, contributions, goals
argument-hint: "[employee name and review period]"
triggers:
  - "performance review"
  - "review prep"
  - "gather review context"
  - "prepare performance review"
  - "annual review"
---

# Performance Review

Preparation tool to gather context for writing performance reviews. Searches vault for meeting notes, project contributions, 1:1 notes, and goal progress. Generates a structured review draft for manager editing.

## When to Trigger

- Manager says "performance review", "review prep", or "annual review"
- HR reminder that review cycle is starting
- Manager asks to gather context on an employee
- Review deadline approaches

## Workflow

### Step 1: Get Review Details

Ask for:

1. **Employee name**
2. **Review period** (e.g., "Q1 2026", "April 2025 - March 2026", "2025")
3. **Review type** — annual, mid-year, promotion review, performance improvement plan, other

### Step 2: Pull Org and Product Context

From ORG.md (already in session context), understand the employee's department. From PRODUCTS.md (already in session context), identify which products their team owns — this helps contextualize their contributions.

### Step 3: Pull Vault Context

Search for all mentions of this person:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{employee_name}" --top-k 10
```

Now search more specifically for:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{name} 1:1 meeting notes" --top-k 5
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{name} project delivered" --top-k 5
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{name} feedback communication" --top-k 3
```

Also read their team file if it exists:
- `~/.second-brain/vault/team/{name}.md` — for role, goals, background

### Step 4: Extract Key Data

From vault search results, compile:

- **Projects delivered** — What did they ship? Impact?
- **Goals progress** — 30-60-90 day or annual goals. Did they hit them?
- **Meetings attended** — Any leadership, presentations, cross-team contributions?
- **Feedback mentions** — Both positive and developmental from 1:1s or meetings
- **Growth areas** — What did they work to improve?
- **Peer collaboration** — Mentions of helping others, teamwork

### Step 5: Generate Review Draft

Create file at `~/.second-brain/vault/hr/reviews/YYYY-MM-DD-<name-slug>-review.md`:

```markdown
# Performance Review: {Name}

**Review Period:** {Start Date} – {End Date}
**Role:** {Title}
**Manager:** {Manager Name}
**Review Type:** {Annual | Mid-year | Promotion | PIP | Other}
**Date Written:** YYYY-MM-DD

---

## Summary

{1-2 sentence overall assessment of performance for the period}

---

## Accomplishments

### Major Projects & Deliverables

- **{Project 1}** — {Description of contribution, scope, outcome, impact}
  - Timeline: {dates}
  - Team: {who they worked with}
  
- **{Project 2}** — {Description of contribution, scope, outcome, impact}
  - Timeline: {dates}
  - Team: {who they worked with}

### Key Metrics / Impact

{If applicable: numbers that show impact — features shipped, bugs fixed, performance improved, customer satisfaction, etc.}

### Cross-Functional Contributions

{Any presentations, mentoring, cross-team initiatives, process improvements they led or participated in}

---

## Goal Progress

### Goals for Review Period

| Goal | Target | Actual | Progress |
|------|--------|--------|----------|
| {Goal 1} | {Target} | {What they achieved} | ✓ Hit / Partial / Missed |
| {Goal 2} | {Target} | {What they achieved} | ✓ Hit / Partial / Missed |
| {Goal 3} | {Target} | {What they achieved} | ✓ Hit / Partial / Missed |

### Overall Goal Achievement

{%} of goals met. {Assessment of whether goals were realistic and if employee achieved them despite changes.}

---

## Strengths & Demonstrated Capabilities

{Organize by competency or theme}

### Technical Excellence / Domain Mastery
- {Specific example of strong work — quote if available}
- {Specific example showing growth in skill}

### Communication & Collaboration
- {Example of effective teamwork or communication}
- {Evidence of helping others or cross-team impact}

### Problem-Solving & Initiative
- {Example of taking ownership and solving a problem}
- {Proactive contributions or process improvements}

### Leadership & Growth Mindset
{If applicable — mentoring, leading projects, taking on stretch assignments}

---

## Areas for Growth & Development

### Current Development Areas

- **{Area 1}** — {What to improve, why it matters}
  - Evidence: {Specific example from meetings/projects}
  - Recommendation: {How to develop — training, mentoring, assignments, etc.}

- **{Area 2}** — {What to improve, why it matters}
  - Evidence: {Specific example}
  - Recommendation: {How to develop}

### Learning Opportunities for Next Period

{Suggest stretch projects, training, cross-functional moves that would help them grow}

---

## Goals for Next Period

### Proposed Goals (30-60-90 or next annual period)

- [ ] {Goal 1} — {Success criteria, timeline}
- [ ] {Goal 2} — {Success criteria, timeline}
- [ ] {Goal 3} — {Success criteria, timeline}

### Development Focus

{1-2 key areas where they should focus growth — may align with "Areas for Growth" above}

---

## Compensation & Promotion Recommendation

**Recommendation:** {On-track | Promotion track | Performance improvement plan | Other}

**Salary/Equity Adjustment:** {If applicable — discuss with HR before finalizing}

**Rationale:** {Why this recommendation — tie to goals, contributions, market factors}

---

## Peer Feedback

{If collected — summarize themes. Do not attribute specific comments unless they agreed to be named.}

---

## Additional Context

**Vault References:**
- [[meetings/{related meeting notes}]]
- [[projects/{relevant project}]]
- [[team/{name}]] — Their profile

---

## Manager Notes (Pre-Review)

{Any private thoughts to remember during the review conversation — tone to set, difficult topics, celebration moments}

---

## Review Conversation

{To be filled in after the 1:1 with the employee}

**Date Discussed:** {Date}
**Employee Feedback:** {Their response to the review}
**Agreed Next Steps:** {What happens next — promotion, development plan, team transition, etc.}
**Sign-off:** Manager: _______ Employee: _______ Date: _______
```

### Step 6: Save to Vault

1. Write draft to `~/.second-brain/vault/hr/reviews/`
2. Display to manager with note:
   > "I've gathered context and drafted a review. Read through it, edit it, fill in the final assessment, then schedule a 1:1 with {Name} to discuss."

### Step 7: Log to Daily

```
- **HH:MM** — Performance review context gathered for {Name} ({period}): [[hr/reviews/YYYY-MM-DD-{name}-review]]
```

### Step 8: Schedule Review Meeting (Optional)

If Calendar is connected:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal create-event --title "Performance Review: {Name}" --duration 60 --with "{employee_email}" --date {suggested date}
```

## Naming Convention

`YYYY-MM-DD-<name-slug>-review.md`

Examples:
- `2026-04-14-sarah-chen-review.md`
- `2026-04-14-q1-review-marcus.md`

## Rules

- **Data-driven** — Use specific examples and metrics from vault, not impressions
- **No surprises** — Comments should reflect ongoing 1:1s and feedback, never new criticism
- **Balance** — Include both strengths and areas to grow; avoid recency bias
- **Confidential** — Keep draft in vault, not shared Asana or email until finalized
- **Manager edits first** — This is a draft for the manager to customize, not the final review
- **Goals are shared** — Manager should have discussed goals with employee at the start of the period
- **Timeline matters** — Don't ask for promotion feedback if they've been in role <6 months
- **Peer feedback sensitivity** — Summarize themes; don't single out one critical peer or create drama
- Performance reviews should reference the products the employee's team owns (from PRODUCTS.md) to properly contextualize their contributions.
