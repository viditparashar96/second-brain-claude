---
description: "Hypothesis-driven debugging — systematic root cause analysis with evidence tracking"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Edit", "Write"]
---

# Debug: Hypothesis-Driven Root Cause Analysis

You are an expert debugger. Follow a strict hypothesis-driven methodology.

## Bug Description

$ARGUMENTS

## Step 1: Characterize

Before touching code, answer the 5W1H:

| Question | Answer |
|----------|--------|
| **What** is the symptom? | {exact error, behavior} |
| **When** did it start? | {after which change/deploy} |
| **Where** does it manifest? | {file, endpoint, env} |
| **Who** is affected? | {scope of impact} |
| **How** to reproduce? | {exact steps} |

Read product context if available:
```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
```

Search for similar past bugs:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "$ARGUMENTS" --top-k 5 2>/dev/null
```

## Step 2: Hypothesize (BEFORE reading code)

**Ultrathink** — Generate 3-7 hypotheses ranked by probability:

```
H1 [{probability}%] — {theory}
   Evidence needed: {what to check}
   Quick test: {fastest way to confirm/eliminate}
```

Rules:
- Start with "what changed recently?" (check git log)
- If PRODUCTS.md loaded, use the product's tech stack to target diagnostics
- Include at least one "not the obvious suspect" hypothesis
- Probabilities must sum to ~100%

## Step 3: Investigate

Order by: `(probability × confidence_if_tested) / time_to_test`

For each hypothesis:
1. State what you're testing
2. Run the diagnostic
3. **Midthink** — update probability based on evidence
4. Mark: CONFIRMED / ELIMINATED / NEEDS MORE DATA

Maintain evidence board:
```
H1 [{old}% → {new}%] — {status}
   ✅ {evidence for}
   ❌ {evidence against}
```

If debugging code: use **bisection** (git bisect or binary search), not linear scan.

## Step 4: Fix

When one hypothesis reaches >90% confidence:
1. Present root cause with evidence
2. **Wait for confirmation**
3. Propose fix options (quick vs proper)
4. Implement approved fix
5. Verify with original reproduction steps

## Step 5: Document

Save bug report to **local project** (if significant):
```bash
mkdir -p docs/bugs
```

Write `docs/bugs/{date}-{slug}.md` with: symptom, root cause, fix, prevention.

Log summary to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('BUG FIX: {product} — {component} — {root cause}. Fix: {fix}. Prevention: {measure}.')
"
```

## Rules

- Hypothesize BEFORE reading code
- Minimum 3 hypotheses
- Track evidence board — update after each test
- Bisect, don't scan linearly
- Verify fix with original repro steps
- Save locally first, log to memory second
