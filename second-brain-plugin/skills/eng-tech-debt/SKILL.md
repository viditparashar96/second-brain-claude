---
name: eng-tech-debt
description: "Tech debt tracker — catalogs debt with business-impact scoring, generates prioritized payoff plans, and tracks trends."
argument-hint: "[add|list|prioritize|report] [description] [--product name] [--severity critical|high|medium|low]"
triggers:
  - "tech debt"
  - "technical debt"
  - "code smell"
  - "refactor"
  - "legacy code"
  - "needs cleanup"
  - "tech debt review"
  - "debt backlog"
  - "maintenance"
  - "cleanup needed"
---

# Tech Debt Tracker & Prioritizer

Catalog → score → prioritize → plan payoff. Business-impact driven.

## Commands

- `add` — Register new debt item
- `list` — View debt registry
- `prioritize` — Score and rank all items
- `report` — Generate leadership report

## Workflow

### ADD
1. Capture: title, product (from PRODUCTS.md), component, type (design/code/dependency/infra/docs/test)
2. Score 1-5: reliability risk, velocity impact, customer impact, security risk, scaling blocker
3. Score effort 1-5: complexity, scope, risk of fix
4. **Priority = (avg_impact × 10) / avg_effort**
   - ≥15: 🔴 Critical | 10-15: 🟠 High | 5-10: 🟡 Medium | <5: 🔵 Low
5. Check if debt blocks strategic priorities from ORG.md → auto-escalate
6. Save `docs/tech-debt/{slug}.md` in local project:
   ```markdown
   ---
   title: "{title}"
   product: "{product}"
   type: "{type}"
   score: {N}
   status: "open"
   ---
   # Tech Debt: {title}
   ## Description
   ## Business Impact (scored)
   ## Proposed Solution
   ## Effort Estimate
   ```
7. Log to memory via `log_note`

### LIST / PRIORITIZE
1. Read all `docs/tech-debt/*.md` in local project
2. Sort by composite score
3. Cross-reference ORG.md priorities — debt blocking priorities gets flagged
4. Present priority matrix

### REPORT
1. Generate leadership summary: totals by severity, strategic blockers, quarterly trend
2. Save report to `docs/tech-debt/report-{date}.md`

## Rules
- Business-impact scoring, not just technical severity
- Debt blocking strategic priorities auto-escalates
- Cross-product debt (shared infra) gets priority multiplier
- Save to **local project** — developers review in repo
- Log summaries to memory
- Product context from PRODUCTS.md — never hardcode
