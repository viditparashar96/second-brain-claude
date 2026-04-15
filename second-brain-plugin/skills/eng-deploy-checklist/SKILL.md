---
name: eng-deploy-checklist
description: "Product-aware deployment checklist — pre-deploy validation, execution, post-deploy verification, and rollback procedures tailored to each product's tech stack."
argument-hint: "[product-name] [version] [--env staging|production] [--type standard|hotfix|rollback]"
triggers:
  - "deploy"
  - "deployment"
  - "release to production"
  - "push to prod"
  - "ship it"
  - "go live"
  - "deploy checklist"
  - "rollback"
  - "hotfix deploy"
  - "deployment runbook"
---

# Deployment Checklist & Runbook

Product-aware deployment: pre-deploy → execute → verify → rollback plan. All checklists generated dynamically from PRODUCTS.md.

## Workflow

### Phase 1: PRE-DEPLOY
1. Identify: product, version, environment, type (standard/hotfix/rollback)
2. Read PRODUCTS.md — **Ultrathink** to generate checklist from the product's actual tech stack:
   - For each component: credentials valid? connectivity verified? version compatible?
3. Standard checks (all products):
   - [ ] Tests pass
   - [ ] Code review approved
   - [ ] Config/env vars correct
   - [ ] Rollback plan documented
   - [ ] Stakeholders notified
4. **🚫 GATE — Go/No-Go decision**

### Phase 2: DEPLOY
1. Generate step-by-step commands from product tech stack
2. Each step: command, verification criteria, estimated time
3. **🚫 GATE at critical steps** (especially DB migrations)

### Phase 3: POST-DEPLOY
1. Verification checklist (generated dynamically):
   - [ ] Smoke tests pass
   - [ ] Error rates normal
   - [ ] Latency within SLA
   - [ ] Monitoring working
2. Monitor 30 min
3. Declare success or trigger rollback

### Phase 4: ROLLBACK (if needed)
1. Present rollback plan
2. **🚫 GATE — Rollback approved**
3. Execute, verify previous version
4. Create incident record → link to `eng-incident-response`

### Phase 5: DOCUMENT (LOCAL FIRST)
1. Save `docs/deployments/{product}-{version}-{date}.md`:
   ```markdown
   ---
   product: "{product}"
   version: "{version}"
   status: "{success|rolled-back}"
   date: "{date}"
   ---
   # Deploy: {product} {version}
   ## Outcome
   ## Issues
   ## Lessons
   ```
2. Update runbook at `docs/runbooks/{product}-deploy.md` if new gotchas found
3. Log to memory via `log_note`

## Rules
- Never deploy without completed checklist
- Checklist generated dynamically from product tech stack — never hardcoded
- Rollback plan BEFORE deploying
- Go/No-Go gate is mandatory
- Failed deployments trigger incident response
- Save locally first, memory second
