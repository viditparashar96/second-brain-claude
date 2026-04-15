---
name: eng-dev-onboarding
description: "Product-aware developer onboarding — generates personalized plans with environment setup, starter tasks, and 30-60-90 day milestones."
argument-hint: "[developer-name] [--product name] [--role frontend|backend|fullstack|devops|ml] [--level junior|mid|senior]"
triggers:
  - "onboard developer"
  - "onboard engineer"
  - "new developer"
  - "new engineer"
  - "dev onboarding"
  - "engineering onboarding"
  - "ramp up new hire"
  - "starter tasks"
  - "onboarding plan"
  - "first week"
---

# Product-Aware Developer Onboarding

Personalized onboarding: profile → plan → track → improve.

## Workflow

### Phase 1: PROFILE
1. Gather: name, role, level, assigned product, start date, buddy
2. Read PRODUCTS.md — dynamically extract the assigned product's tech stack, architecture, known issues, dependencies
3. Read ORG.md — company context, values, strategic priorities
4. Read project docs (`README.md`, `CONTRIBUTING.md`, `docs/`)
5. Search memory for past onboarding notes and common pitfalls
6. **🚫 GATE — Profile confirmed**

### Phase 2: GENERATE PLAN
**Ultrathink** — Create personalized plan based on product tech stack, role, and level:

#### Week 1: Environment & Orientation
- Day 1: HR, access, Slack, meet buddy
- Day 2: Dev environment (generate setup steps from product's actual tech stack in PRODUCTS.md)
- Day 3: Codebase walkthrough with buddy
- Day 4-5: First contribution (level-adjusted)

#### 30-Day: Productive Contributor
- Build/run stack, 3-5 PRs, debug independently

#### 60-Day: Independent Contributor
- Design features, review PRs, understand competitive landscape

#### 90-Day: Full Team Member
- Architecture proposals, mentor others, ship significant feature

#### Starter Tasks (progressive, level-adjusted)
- Junior: fix documented bug → add test → small feature
- Mid: add tests → implement feature → review PR
- Senior: review PR → propose improvement → lead feature

### Phase 3: SAVE (LOCAL FIRST)
1. Save `docs/onboarding/{name-slug}.md` in local project
2. Create calendar events for milestone check-ins (30/60/90)
3. Create tasks for buddy responsibilities
4. Log summary to memory via `log_note`

### Phase 4: FEEDBACK (at milestones)
1. Collect: what was confusing, what was missing, rating 1-5
2. Log improvements to memory for next onboarding

## Rules
- Tech stack from PRODUCTS.md — never hardcode tools or setup steps
- Personalized by role, level, AND product
- Starter tasks curated and progressive
- Include competitive context (engineers should understand WHY)
- Save locally first, memory second
