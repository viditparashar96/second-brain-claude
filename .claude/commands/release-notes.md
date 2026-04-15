---
description: "Generate release notes from git history — categorize changes, produce audience-appropriate docs"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# Release Notes Generator

Generate structured release notes from git history.

## Parameters

$ARGUMENTS

## Step 1: Scope

```bash
git tag --sort=-v:refname | head -10
PREV_TAG=$(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo "initial")
```

```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
```

## Step 2: Extract

```bash
git log ${PREV_TAG}..HEAD --oneline --no-merges
git diff --stat ${PREV_TAG}..HEAD
```

## Step 3: Categorize

**Ultrathink** — Parse commits into:
- 💥 Breaking Changes
- ✨ Features
- 🐛 Bug Fixes
- ⚡ Performance
- 🔒 Security
- 📚 Docs
- ♻️ Refactoring
- 📦 Dependencies

Map technical changes to product features using PRODUCTS.md context.

Present. **Wait for confirmation.**

## Step 4: Generate (LOCAL FIRST)

```bash
mkdir -p docs/releases
```

Save to `docs/releases/{version}.md`:

```markdown
# {Product} {version} Release Notes

**Date:** {YYYY-MM-DD}
**Previous:** {prev-version}

## Highlights
{2-3 sentence summary}

## 💥 Breaking Changes
### {title}
{description + migration guide}

## ✨ Features
### {title}
{description}

## 🐛 Bug Fixes
- **{title}** — {description}

## ⚡ Performance
- **{title}** — {description}

## Contributors
{list}
```

If customer-facing audience: generate a second version without implementation details.

Log to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('RELEASE: {product} {version} — {highlights}. Breaking: {yes/no}.')
"
```

## Rules

- Git is source of truth — don't fabricate
- Breaking changes MUST have migration guides
- Security fixes don't expose vuln details in customer notes
- Save locally, memory second
- Publish to GitHub only with explicit approval
