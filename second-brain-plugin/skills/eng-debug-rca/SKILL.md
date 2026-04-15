---
name: eng-debug-rca
description: "Hypothesis-driven debugging and root cause analysis — systematic investigation with evidence tracking, bisection, and fix verification."
argument-hint: "[bug-description] [--repo path] [--logs path] [--severity P0-P3]"
triggers:
  - "debug"
  - "root cause"
  - "RCA"
  - "why is this failing"
  - "bug"
  - "error"
  - "crash"
  - "investigate"
  - "figure out why"
  - "not working"
  - "broken"
  - "regression"
---

# Hypothesis-Driven Debug & RCA

Systematic debugging: characterize → hypothesize → investigate → fix → document. Evidence-based, never guess.

## Workflow

### Phase 1: CHARACTERIZE
1. Gather 5W1H: What (symptom), When (started), Where (component), Who (affected), How (reproduce)
2. Read PRODUCTS.md — match to product, pull tech stack dynamically
3. Search memory for similar past bugs
4. **🚫 GATE — Reproduction confirmed**

### Phase 2: HYPOTHESIZE (before reading code)
1. **Ultrathink** — Generate 3-7 hypotheses ranked by probability
2. Each hypothesis: probability%, evidence needed, quick test
3. Include "what changed recently" as primary suspect
4. Order investigation by: `(probability × confidence) / time_to_test`

### Phase 3: INVESTIGATE
1. Test hypotheses most-likely-first
2. For each: state test → run diagnostic → **Midthink** → update probability
3. Maintain evidence board:
   ```
   H1 [45% → 80%] — LIKELY ✅ evidence1 ❌ evidence2
   H2 [25% → 5%]  — ELIMINATED
   ```
4. For code bugs: use **bisection** (git bisect), not linear scan
5. Converge when one hypothesis >90%
6. **🚫 GATE — Root cause confirmed**

### Phase 4: FIX
1. Propose options (quick vs proper, with risk/reversibility)
2. **🚫 GATE — Fix approach approved**
3. Implement, verify with original repro steps
4. Test adjacent functionality for regressions

### Phase 5: DOCUMENT (LOCAL FIRST)
1. Save `docs/bugs/{date}-{slug}.md` in local project:
   ```markdown
   ---
   title: "{title}"
   date: "{date}"
   product: "{product}"
   root_cause: "{summary}"
   ---
   # {title}
   ## Symptom
   ## Root Cause
   ## Fix Applied
   ## Prevention
   ```
2. Log one-line summary to memory via `log_note`

## Rules
- Hypothesize BEFORE reading code
- Minimum 3 hypotheses, track evidence for each
- Bisect, don't scan linearly
- Verify fix with original repro steps
- Save locally first, memory second
- Product context from PRODUCTS.md — never hardcode
