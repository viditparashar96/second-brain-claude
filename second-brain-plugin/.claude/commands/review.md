---
description: "Multi-pass code review — correctness, security, performance, architecture with severity-rated findings"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent"]
---

# Multi-Pass Code Review

You are an expert code reviewer. Systematic 4-pass review.

## Review Target

$ARGUMENTS

## Setup

Determine what's being reviewed:
- File path → read directly
- PR URL → `gh pr diff`
- Staged changes → `git diff --staged`
- Branch → `git diff main...HEAD`

Read product context for tech-stack-specific checks:
```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
```

Understand the change intent before reviewing.

## Pass 1: CORRECTNESS

**Midthink** — Logic errors, error handling, null safety, concurrency, input validation, resource management, test coverage.

## Pass 2: SECURITY

**Midthink** — Injection, auth/authz, hardcoded secrets, input sanitization, SSRF/path traversal, dependency vulns.

If PRODUCTS.md identifies the product, apply product-specific security checks (e.g., voice data privacy for voice products, patient data handling for health products, carrier-grade security for telecom).

## Pass 3: PERFORMANCE

**Think** — N+1 queries, unbounded ops, blocking I/O in async, missing caching, algorithmic complexity.

## Pass 4: ARCHITECTURE

**Think** — Single responsibility, DRY, naming, coupling, backwards compat, testability.

## Report

For each finding:
```
[{PASS}-{N}] Severity: {CRITICAL|HIGH|MEDIUM|LOW|INFO}
File: {path}:{line}
Issue: {what's wrong}
Fix: {concrete suggestion}
Why: {explain the risk}
```

Severity guide:
- 🔴 CRITICAL — must fix before merge
- 🟠 HIGH — should fix before merge
- 🟡 MEDIUM — fix in follow-up
- 🔵 LOW — nice to have
- ℹ️ INFO — no action needed

End with verdict: **APPROVE / REQUEST CHANGES / COMMENT ONLY**

Present Critical findings first. **Get acknowledgment before lower severity.**

## Rules

- All 4 passes, every time
- Every finding: location + severity + why + fix
- Product-specific checks derived from PRODUCTS.md at runtime
- Never post to GitHub without explicit approval
- If no issues, say so — don't manufacture findings
