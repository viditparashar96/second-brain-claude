---
name: org-manager
description: Set up and manage organization profile (ORG.md) — company info, departments, goals
argument-hint: "{setup|update|view}"
triggers:
  - "setup organization"
  - "org profile"
  - "company info"
  - "update org"
  - "organization setup"
  - "company profile"
  - "set up company"
---

# Organization Manager

Set up and manage your organization's profile (ORG.md). This is the company-level identity file — like USER.md is for the individual, ORG.md is for the organization. Loaded into every session so all skills have company context.

## When to Trigger

- First-time setup: user wants to configure their organization's profile
- User asks to update company info, departments, or strategic goals
- User says "setup organization", "company profile", or "update org"
- During onboarding when a new org is adopting the plugin

## Workflow

### Command: `setup` — Initial Organization Setup

1. **Gather company details** — Ask for:
   - Organization name
   - Industry
   - Headquarters location
   - Founded year (optional)
   - Website
   - Brief description (1-2 sentences)

2. **Gather department info** — Ask for:
   - Which departments exist (Engineering, Sales, Product, HR, Ops, Marketing, etc.)
   - Department heads (names and roles)
   - Approximate team sizes

3. **Gather global presence** (if applicable):
   - Office locations
   - Key markets / regions
   - Number of clients / users

4. **Gather strategic context**:
   - Current company OKRs or strategic priorities
   - Key metrics the org tracks (ARR, users, NPS, etc.)
   - Company values or culture notes

5. **Generate ORG.md** — Create the file at `~/.second-brain/vault/ORG.md` using the template from `${CLAUDE_PLUGIN_ROOT}/templates/ORG.md`, filling in all collected information

6. **Prompt for products** — Ask: "Want to add your products now? Run `/second-brain:product-manager add` to start building the product registry."

7. **Log to daily** — Append: `- **HH:MM** — [ORG] Organization profile created: {org name}`

### Command: `update` — Update Organization Info

1. **Read current ORG.md** from `~/.second-brain/vault/ORG.md`
2. **Ask what changed** — departments, goals, metrics, team structure
3. **Edit ORG.md** with the new information
4. **Log to daily** — Append: `- **HH:MM** — [ORG] Updated: {what changed}`

### Command: `view` — View Organization Profile

1. **Read and display ORG.md** from `~/.second-brain/vault/ORG.md`
2. **Show summary** — org name, department count, product count (from PRODUCTS.md), key goals

## Rules

- **ORG.md loads into every session.** Keep it concise — under 150 lines ideally.
- **Don't duplicate USER.md info.** ORG.md is company-level, USER.md is individual-level.
- **Strategic goals should be current.** Update quarterly at minimum.
- **Department table should reflect reality.** Update when teams change.
- **This file is the company identity.** All department skills use it for organizational context — sales knows who they work for, HR knows the departments, product knows the strategic priorities.

## Integration with Other Skills

- **Setup skill** (`/second-brain:setup`) should prompt for org setup as part of onboarding
- **Product Manager** (`/second-brain:product-manager`) manages PRODUCTS.md separately but complements ORG.md
- **All department skills** read ORG.md automatically via session start injection
- **Stakeholder updates** pull strategic goals from ORG.md to frame progress
- **Onboarding checklists** pull department structure from ORG.md
