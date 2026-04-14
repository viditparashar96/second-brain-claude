---
name: eng-architecture-decision
description: "Architecture Decision Record creator — structured trade-off analysis with weighted scoring, option evaluation, and decision documentation."
argument-hint: "[decision-title] [--context description] [--options A,B,C]"
triggers:
  - "architecture decision"
  - "ADR"
  - "should we use"
  - "tech choice"
  - "design decision"
  - "trade-off"
  - "tradeoff"
  - "evaluate options"
  - "which approach"
  - "compare architectures"
  - "system design"
  - "RFC"
---

# Architecture Decision Record Creator

Structured decision-making: frame → evaluate → decide → document. Rigorous trade-off analysis with organizational context.

## Workflow

### Phase 1: FRAME
1. Read project docs (`docs/adrs/`) and org context (PRODUCTS.md, ORG.md) — dynamically identify affected products and constraints
2. Search memory for prior ADRs and related decisions
3. Define: decision title, affected products, weighted drivers, Type 1 (irreversible) vs Type 2 (reversible)
4. **🚫 GATE — Framing confirmed**

### Phase 2: EVALUATE
1. **Ultrathink** — Build weighted comparison matrix:
   ```
   | Criteria (weight)     | Option A | Option B | Option C |
   |-----------------------|----------|----------|----------|
   | {driver1} ({weight}%) | ★★★★☆   | ★★★☆☆   | ★★★★★   |
   | Weighted Score        | X.XX     | X.XX     | X.XX     |
   ```
2. For each option: pros, cons, hidden costs (migration, lock-in, training)
3. Top 3 risks per option with mitigations
4. Strategic fit against ORG.md priorities

### Phase 3: DECIDE
1. Present recommendation: which option, why, trade-offs accepted/rejected
2. **🚫 GATE — Decision approved**

### Phase 4: DOCUMENT (LOCAL FIRST)
1. Save `docs/adrs/ADR-{NNN}-{slug}.md` in local project:
   ```markdown
   ---
   adr_id: "ADR-{NNN}"
   title: "{title}"
   date: "{date}"
   status: "accepted"
   products: ["{product}"]
   ---
   # ADR-{NNN}: {title}
   ## Status
   ## Context
   ## Decision Drivers
   ## Options Considered
   ## Decision
   ## Consequences (Positive / Negative / Neutral)
   ## Review Trigger
   ```
2. Log one-line summary to memory via `log_note`

## Rules
- Weighted criteria — no gut-feeling comparisons
- Every option gets fair analysis (no strawmen)
- Type 1 = full ADR; Type 2 = lightweight
- Save to **local project `docs/adrs/`**
- Product/org context read dynamically — never hardcode
