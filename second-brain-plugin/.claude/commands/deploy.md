---
description: "Deployment checklist — product-specific pre-deploy validation, execution, verification, and rollback"
allowed-tools: ["Read", "Glob", "Grep", "Bash", "Agent", "Write"]
---

# Deployment Checklist

You are a deployment engineer. Generate and run a product-specific deployment checklist.

## Deployment Info

$ARGUMENTS

## Step 1: Context

```bash
cat ~/.second-brain/vault/PRODUCTS.md 2>/dev/null
```

Determine: product, version, environment (staging/prod), type (standard/hotfix/rollback).

## Step 2: Pre-Deploy Checklist

**Ultrathink** — Generate a checklist dynamically from the product's tech stack in PRODUCTS.md.

For each component in the tech stack, add relevant checks:
- API keys/credentials valid?
- Service connectivity verified?
- Version compatibility confirmed?

Standard checks (all products):
- [ ] Tests pass
- [ ] Code review approved
- [ ] Config/env vars correct for target environment
- [ ] Rollback plan documented (see Step 5)
- [ ] Stakeholders notified
- [ ] On-call engineer identified

Present checklist. **Wait for go/no-go.**

## Step 3: Deploy

Generate step-by-step commands. Each step:
1. Exact command
2. Verification criteria
3. Estimated time

**Confirm at every critical step** (especially DB migrations).

## Step 4: Post-Deploy

- [ ] Smoke tests pass
- [ ] Error rates normal
- [ ] Latency within SLA
- [ ] Monitoring working

Monitor for 30 min. Report status.

## Step 5: Rollback (if needed)

1. Present rollback plan
2. **Get approval**
3. Execute
4. Verify previous version
5. Create incident record → `/project:incident`

## Step 6: Document (LOCAL FIRST)

```bash
mkdir -p docs/deployments
```

Save to `docs/deployments/{product}-{version}-{date}.md`:

```markdown
---
product: "{product}"
version: "{version}"
environment: "{env}"
date: "{date}"
status: "{success|rolled-back}"
duration: "{time}"
---

# Deploy: {product} {version}

## Outcome: {status}
## Issues: {any problems}
## Lessons: {what to do differently}
```

Log to memory:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from memory_search import log_memory
log_memory('DEPLOY: {product} {version} → {env} — {status}. Duration: {time}.')
"
```

## Rules

- Never deploy without completed checklist
- Never deploy without go/no-go confirmation
- Rollback plan BEFORE deploying
- Checklist generated dynamically from product tech stack
- Save locally first, memory second
