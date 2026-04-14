---
name: eng-release-notes
description: "Git-driven release note generator — analyzes commits and PRs, categorizes changes, produces audience-appropriate documentation."
argument-hint: "[version] [--from tag|commit] [--to tag|commit] [--audience internal|customer|all]"
triggers:
  - "release notes"
  - "changelog"
  - "what changed"
  - "what shipped"
  - "version bump"
  - "new release"
  - "prepare release"
  - "release summary"
  - "what's in this release"
---

# Git-Driven Release Notes

Analyze git history → categorize changes → generate audience-appropriate release docs.

## Workflow

### Phase 1: GATHER
1. Determine scope: product, version, tag range
2. Extract git history: `git log`, `git diff --stat`, merge commits
3. Fetch PR data if GitHub connected (`list_prs` MCP tool)
4. Read PRODUCTS.md — map changes to product features dynamically

### Phase 2: CATEGORIZE
1. **Ultrathink** — Parse commits into: 💥 Breaking, ✨ Features, 🐛 Fixes, ⚡ Perf, 🔒 Security, 📚 Docs, ♻️ Refactoring, 📦 Deps
2. Present categorization
3. **🚫 GATE — Categories confirmed**

### Phase 3: GENERATE (LOCAL FIRST)
1. Save `docs/releases/{version}.md` in local project:
   ```markdown
   # {Product} {version}
   **Date:** {date} | **Previous:** {prev}
   ## Highlights
   ## 💥 Breaking Changes (with migration guides)
   ## ✨ Features
   ## 🐛 Bug Fixes
   ## ⚡ Performance
   ## Contributors
   ```
2. If customer-facing: generate separate version (no implementation details, value-focused)
3. **🚫 GATE — Notes approved before publishing**

### Phase 4: DISTRIBUTE (on request)
1. GitHub release: `gh release create` — requires approval
2. Draft stakeholder email via `draft_email` MCP tool — requires approval
3. Log summary to memory via `log_note`

## Rules
- Git is source of truth — don't fabricate changes
- Breaking changes MUST have migration guides with before/after
- Security fixes don't expose vuln details in customer notes
- Save locally first, memory second
- Publish only with explicit approval
