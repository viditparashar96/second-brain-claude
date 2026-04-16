---
name: code-review
description: Run an initial automated code review sweep on GitHub PRs
triggers:
  - "review this PR"
  - "code review"
  - "check this pull request"
  - "review PR #"
---

# Code Review

Use this skill to perform an initial code review sweep on GitHub pull requests. Fetches the PR diff via the GitHub integration, evaluates against the review checklist, and posts a review comment.

## When to Trigger

- User asks to review a PR (by number or URL)
- Heartbeat detects PRs awaiting Vidit's review
- User says "code review", "review this PR", or "check PR #N"

## Workflow

1. **Identify the PR** — Extract repo and PR number from user input or heartbeat context
2. **Fetch the diff** — Run: `.venv/bin/python .claude/scripts/integrations/query.py github diff <PR_NUMBER> --repo <OWNER/REPO>`
3. **Load checklist** — Read `references/review-checklist.md` for evaluation criteria
4. **Analyze each changed file** against the checklist categories:
   - Correctness
   - Edge cases
   - Naming and clarity
   - Security
   - Test coverage
5. **Draft review comments** — For each issue found, note the file, line context, and what to fix
6. **Post the review** — Run: `.venv/bin/python .claude/scripts/integrations/query.py github review <PR_NUMBER> --repo <OWNER/REPO> --body "<review text>" --event COMMENT`
7. **Log to daily** — Append: `- **HH:MM** — Reviewed PR #N on <repo>: <summary>`

## Rules

- **Always post as COMMENT**, never APPROVE or REQUEST_CHANGES — Vidit makes the final call
- Skip style nits (formatting, whitespace) — focus on logic, correctness, and security
- If the PR is too large (>20 files), summarize high-risk files and suggest splitting
- If you can't determine context (missing test files, unclear intent), say so rather than guessing
- Reference specific line numbers and file paths in comments
- Be constructive — suggest fixes, not just problems

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
