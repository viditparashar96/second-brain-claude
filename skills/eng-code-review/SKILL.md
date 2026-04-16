---
name: eng-code-review
description: "Interactive multi-pass code review — correctness, security, performance, architecture with severity-rated findings and actionable fixes."
argument-hint: "[PR-url|diff|file-path] [--focus security|perf|arch|all] [--product name]"
triggers:
  - "code review"
  - "review this PR"
  - "review my code"
  - "review this diff"
  - "check my code"
  - "PR review"
  - "pull request review"
  - "code quality"
  - "security review"
  - "is this code good"
---

# Interactive Multi-Pass Code Review

4-pass review: correctness → security → performance → architecture. Severity-rated findings with actionable fixes.

## Workflow

### Setup
1. Determine source: file path, PR URL (`gh pr diff`), staged changes (`git diff --staged`), or branch diff
2. Read PRODUCTS.md — identify product and apply tech-stack-specific checks dynamically
3. Understand change intent (PR description, commit messages)

### Pass 1: CORRECTNESS
**Midthink** — Logic errors, error handling, null safety, concurrency, input validation, resource management, test coverage.

### Pass 2: SECURITY
**Midthink** — Injection, auth/authz, hardcoded secrets, input sanitization, SSRF/path traversal, dependency vulns.
Apply product-specific security checks based on the product type identified from PRODUCTS.md (e.g., data privacy for voice/health, carrier-grade for telecom, transaction integrity for gaming).

### Pass 3: PERFORMANCE
**Think** — N+1 queries, unbounded ops, blocking I/O in async, missing caching, algorithmic complexity.

### Pass 4: ARCHITECTURE
**Think** — Single responsibility, DRY, naming, coupling, backwards compat, testability.

### Report
Each finding:
```
[{PASS}-{N}] Severity: {CRITICAL|HIGH|MEDIUM|LOW|INFO}
File: {path}:{line}
Issue: {what's wrong}
Fix: {concrete suggestion with code}
Why: {explain the risk}
```

Severity:
- 🔴 CRITICAL — must fix before merge
- 🟠 HIGH — should fix before merge
- 🟡 MEDIUM — fix in follow-up
- 🔵 LOW — nice to have
- ℹ️ INFO — learning opportunity

Present Critical first. **🚫 GATE — Acknowledge critical findings before lower severity.**

Verdict: **APPROVE / REQUEST CHANGES / COMMENT ONLY**

## Rules
- All 4 passes, every time
- Every finding: location + severity + why + concrete fix
- Product-specific checks derived dynamically from PRODUCTS.md
- Never post to GitHub without explicit approval
- If no issues, say so — don't manufacture findings

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
