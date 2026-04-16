---
name: hr-onboarding-checklist
description: Generate role-specific onboarding plans for new hires with phased checklists
argument-hint: "[new hire name, role, department, start date]"
triggers:
  - "onboarding checklist"
  - "new hire plan"
  - "onboarding plan"
  - "prepare onboarding"
  - "new team member"
---

# Onboarding Checklist

Generate comprehensive, phased onboarding plans for new hires. Includes pre-arrival setup, week 1 orientation, month 1 training, and 30-60-90 day goals. Pulls team and project context from vault.

## When to Trigger

- HR or manager mentions a new hire start date
- User says "onboarding checklist", "new hire plan", or "prepare onboarding"
- New hire is added to team/ vault
- Manager wants structured onboarding timeline

## Workflow

### Step 1: Gather New Hire Info

Ask for (or extract from context):

1. **New hire name** (first and last)
2. **Role/title**
3. **Department/team**
4. **Start date** (YYYY-MM-DD)
5. **Manager name**
6. **Reporting structure** (any direct reports? who do they report to?)

### Step 2: Pull Vault Context

Search for team and project context:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "team {department} context" --top-k 2
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{role} responsibilities" --top-k 2
```

Read the new hire's manager file if it exists:
- `~/.second-brain/vault/team/{manager-name}.md`

This informs what tools, systems, and projects matter for their role.

### Step 3: Pull Org and Product Context

From ORG.md (already in session context), identify the department structure. From PRODUCTS.md (already in session context), identify which products the new hire's team/department owns, so the onboarding plan includes product-specific training, repos, and documentation.

### Step 4: Generate Onboarding Plan

Create file at `~/.second-brain/vault/hr/onboarding/YYYY-MM-DD-<name-slug>.md`:

```markdown
# Onboarding Plan: {Name}

**Role:** {Title}
**Team:** {Department}
**Start Date:** YYYY-MM-DD
**Manager:** {Manager Name}
**Direct Reports:** {List or None}

---

## Pre-Arrival (1-2 weeks before)

### IT & Accounts
- [ ] Create email account (format: firstname.lastname@company.com)
- [ ] Set up Slack workspace access
- [ ] Provision laptop & peripherals — order by {date}
- [ ] Create GitHub account (if engineering role)
- [ ] Add to Asana workspace
- [ ] Set up Google Calendar & Drive
- [ ] Create shared drive folder: `Team/{Department}/{Name}`

### Workspace & Admin
- [ ] Reserve desk/workspace location
- [ ] Order welcome package (office supplies, swag, coffee beans, etc.)
- [ ] Prepare workspace (desk setup, monitor, keyboard)
- [ ] Generate offer letter & onboarding documents
- [ ] Create team calendar event: "Welcome {Name}!"
- [ ] Brief team on start date, background, role

### Manager Tasks
- [ ] Schedule 1:1 for Day 1 (1 hour)
- [ ] Assign onboarding buddy/buddy pair — {Name(s)}
- [ ] Prepare role documentation
- [ ] Review goals framework for 30-60-90 day setup

---

## Week 1: Orientation & Tools

### Day 1 (Start Day)
- [ ] **Morning:** Meet & greet with manager (30 min)
- [ ] **Morning:** IT setup — test laptop, email, phone, Slack, systems access
- [ ] **Afternoon:** Team meet & greet (30-45 min group call or in-person)
- [ ] **Afternoon:** Building/workspace tour with buddy
- [ ] **End of day:** Low-key 1:1 with manager — reassure, ask questions
- [ ] **Assigned reading:** [[hr/policies/company-handbook]] (summary)

### Days 2-3: Systems & Context
- [ ] Complete all IT onboarding steps
- [ ] Asana walkthrough with buddy — explore team project board
- [ ] GitHub/repo access (engineering) or document systems walkthrough
- [ ] Read team working norms & recent decisions: [[team/{department}]]
- [ ] Attend standup or team sync if applicable
- [ ] Map out 1:1 cadence with manager (weekly, Mondays 10am, etc.)

### Days 4-5: First Tasks & Culture
- [ ] Attend company meeting / all-hands if scheduled
- [ ] Read onboarding docs: culture, values, code of conduct
- [ ] Join relevant Slack channels (watercooler, company-news, {team}, etc.)
- [ ] Schedule coffee chats with 2-3 cross-functional peers (buddy helps arrange)
- [ ] Review [[projects/{relevant-project}]] if applicable
- [ ] Assign first small task (bug fix, documentation, small feature)

### Week 1 Outcomes
- [ ] Systems all working
- [ ] Understands team structure and current projects
- [ ] Has met manager, buddy, and direct team members

---

## Month 1: Training & Ramp

### Week 2
- [ ] Deep dive on role responsibilities with manager (1-2 hours)
- [ ] Read codebase README / onboarding docs (if applicable)
- [ ] First code/work review with team lead
- [ ] Attend all recurring team meetings
- [ ] Lunch with buddy or team member each day

### Week 3-4
- [ ] Pair programming or shadowing sessions (2-3 sessions)
- [ ] Complete one small independent task
- [ ] Review any role-specific training material (domain knowledge, tools, processes)
- [ ] First performance check-in with manager: "How's it going? What do you need?"
- [ ] Attend cross-functional team meetings (design, product, etc. if applicable)

### Month 1 Outcomes
- [ ] Can independently complete small assigned tasks
- [ ] Understands team processes and communication norms
- [ ] Has started building relationships across team
- [ ] Knows who to ask for help and what documentation exists

---

## 30-60-90 Day Goals

### 30 Days (Immersion)
**Goal:** Understand role, team, and systems

- Complete all core training
- Deliver 3-5 small tasks independently
- Participate in team meetings with understanding
- Build initial relationships with manager, buddy, and teammates

### 60 Days (Productivity)
**Goal:** Contribute independently to team goals

- Lead 1-2 projects/features of moderate scope
- Proactive problem-solving (identify issues, propose solutions)
- Active in team decisions and brainstorms
- Building strong working relationships

### 90 Days (Value)
**Goal:** Demonstrated capability and alignment

- Delivered measurable impact to team/company
- Self-directed task identification and execution
- Mentoring or supporting junior team members (where applicable)
- Proposal or initiative showing domain understanding

---

## Manager Checkpoints

- **End of Week 1:** Quick check-in — how's the setup? Any blockers?
- **End of Week 2:** How's the learning going? Pace okay?
- **Week 3-4:** Feedback on first tasks — what went well, what to improve?
- **30-day review:** Formal check-in — are we on track for 30-day goals?
- **60-day review:** Mid-point review — progress toward role mastery?
- **90-day review:** Formal performance review — ready to move off "onboarding" status?

---

## New Hire Team File

Create `~/.second-brain/vault/team/{Name}.md`:

```markdown
# {Name}

**Title:** {Role}
**Department:** {Team}
**Start Date:** YYYY-MM-DD
**Manager:** [[team/{Manager}]]
**Direct Reports:** {List if applicable}
**Onboarding Plan:** [[hr/onboarding/YYYY-MM-DD-{name-slug}]]

## Background

{Brief professional background — where they came from, key experience}

## Role

{Description of their role and key responsibilities}

## Goals (30-60-90)

- **30 Days:** {goal}
- **60 Days:** {goal}
- **90 Days:** {goal}

## Onboarding Progress

- [ ] Systems setup
- [ ] Week 1 orientation complete
- [ ] First task delivered
- [ ] 30-day review passed
- [ ] 60-day review passed
- [ ] 90-day review passed (fully ramped)

## Notes

{Any special notes — previous projects, skills to leverage, development areas}
```

---

## Asana Integration (Optional)

If Asana is connected, ask:
> "Want me to create onboarding tasks in Asana with due dates?"

If yes:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task --name "Pre-arrival: IT setup for {Name}" --due "{start-date minus 14 days}" --notes "Email, laptop, Slack, GitHub"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task --name "30-day onboarding review: {Name}" --due "{start-date plus 30 days}" --notes "Manager: Check progress on goals"
```

## Naming Convention

`YYYY-MM-DD-<name-slug>.md`

Examples:
- `2026-04-14-sarah-chen.md`
- `2026-04-20-michael-rodriguez.md`

## Rules

- **Customize by role** — Engineering roles add repo/deploy info; sales roles add CRM setup; designers add design tool access
- **Adapt to company size** — Smaller orgs may skip some formality; larger orgs may add more checkpoint reviews
- **Manager owns execution** — They delegate to IT, buddy, team lead; this is their playbook
- **Track progress** — Update team/{Name}.md as milestones are hit
- **Feedback loop** — After the new hire's 30-day review, update this template if something worked better or is missing
- Onboarding plans must include product-specific context from PRODUCTS.md — which products the team owns, key repos, and stakeholders.

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
