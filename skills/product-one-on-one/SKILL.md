---
name: product-one-on-one
description: Prepare for and capture 1:1 meetings with team members
argument-hint: "[team-member-name]"
triggers:
  - "prep for 1:1"
  - "1:1 prep"
  - "prepare 1:1"
  - "one-on-one"
  - "1on1"
  - "1:1 notes"
  - "capture 1:1"
  - "1:1 with"
---

# One-on-One

Comprehensive 1:1 meeting prep and capture tool. Prepares structured talking points before meetings and captures outcomes afterward with growth and accountability tracking.

## When to Trigger

- User has a scheduled 1:1 with a team member and wants prep
- Preparing talking points before a 1:1 conversation
- Capturing notes and action items after a 1:1 meeting
- Monthly/quarterly check-ins with direct reports
- Career development and growth discussions
- Performance feedback and accountability check-ins

## Workflow

### PREP PHASE

1. **Extract team member name** — Parse from user input (e.g., "prep for 1:1 with Sarah")

2. **Load team member context** — Read vault file:
   ```bash
   cat ~/.second-brain/vault/team/<name-slug>.md
   ```
   Extract: role, recent projects, career goals, known challenges, past feedback

3. **Search for recent activity** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<name> work progress projects" --top-k 5
   ```
   Find: recent accomplishments, decisions made, growth areas mentioned

4. **Check daily log mentions** — Search for their name in daily log:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<name>" --path "daily" --top-k 3
   ```
   Extract: recent wins, challenges, blockers logged

5. **Fetch their Asana tasks** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana search "assignee:<name>" --status "Not Started,In Progress"
   ```
   List: open tasks, overdue work, blocked items

6. **Search vault for action items** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<name> action items from:1:1" --top-k 5
   ```
   Extract: items from last 1:1, commitments made, progress on those items

7. **Generate prep agenda** with sections:
   - **Wins to Celebrate** — Recent accomplishments, code reviews shipped, milestones met
   - **Open Action Items** — From last 1:1, current status, blockers
   - **Project Status** — Active projects, progress, any risks
   - **Blockers & Support** — What's preventing progress, where they need help
   - **Growth Areas** — Skill development, stretch assignments, career goals
   - **Feedback & Recognition** — Specific praise for recent work, areas for growth
   - **This Period's Priorities** — What's on their plate, upcoming deadlines
   - **Talking Points** — 3-5 topics to ensure we cover

8. **Save prep file** to:
   ```bash
   ~/.second-brain/vault/meetings/YYYY-MM-DD-1on1-prep-<name-slug>.md
   ```

9. **Display to user** — Present structured prep with talking points

### CAPTURE PHASE

10. **After 1:1, capture notes** — User provides notes or transcript

11. **Structure meeting notes** with sections:
    - **Date & Time** — When meeting occurred
    - **Wins Celebrated** — What we praised, accomplishments noted
    - **Challenges Discussed** — Blockers they're facing, support needed
    - **Action Items** — Commitments from both sides with due dates
    - **Growth & Development** — Career aspirations, learning needs, stretch opportunities
    - **Feedback** — Constructive input shared, growth areas identified
    - **Next Topics** — What to discuss next time

12. **Save meeting notes** to:
    ```bash
    ~/.second-brain/vault/meetings/YYYY-MM-DD-1on1-<name-slug>.md
    ```

13. **Update team member vault file** — Append latest 1:1 notes, updated career goals, action items:
    ```bash
    cat ~/.second-brain/vault/team/<name-slug>.md
    ```
    Add: date of meeting, key outcomes, updated status

14. **Create Asana tasks** (if connected) — For action items assigned to team member:
    ```bash
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create "<action-item>" --assignee "<name>" --due-date "<due-date>"
    ```

15. **Log to daily log**:
    ```bash
    - **HH:MM** — [1:1] <name> — wins: [brief]; blockers: [brief]; action items: [count]
    ```

## Rules

- Keep 1:1 notes focused on person's growth, blockers, and development — not just task status
- Action items should be specific, assigned, and have due dates
- Celebrate wins explicitly — people need to hear what they're doing well
- Growth conversation should tie to career development goals in team member's vault file
- Use team member's vault file to understand individual context (promotions, learning goals, challenges)
- One-on-ones should be 30-60 minutes, deep not wide — cover fewer topics thoroughly
- Link to related projects and meetings using [[wiki-links]]
- Outcomes from 1:1s should surface in team updates and performance reviews

## Templates

### Prep Template

```markdown
# 1:1 Prep: [Name] — [Date]

**Role**: [title]  
**Manager**: [your name]  
**Last 1:1**: [YYYY-MM-DD]

## Wins to Celebrate

- [Recent accomplishment with dates/details]
- [Specific contribution or growth]

## Open Action Items

- [ ] [Item from last 1:1] — Status: [on-track|blocked]
- [ ] [Item from last 1:1] — Status: [on-track|blocked]

## Current Projects & Status

- [Project name]: [progress, any risks]
- [Project name]: [progress, any risks]

## Known Blockers

- [What's preventing progress]
- [Support they've requested]

## Growth Opportunities

- [Career goal they mentioned]
- [Skill they want to develop]
- [Stretch assignment idea]

## Talking Points

1. [Topic from action item or blocker]
2. [Topic from recent accomplishment]
3. [Topic from growth goal]
4. [Topic from ongoing project]
5. [Topic for feedback or career development]

---
[[team/<name-slug>]]
```

### Meeting Notes Template

```markdown
# 1:1: [Name] — [YYYY-MM-DD]

**Attendees**: [manager], [name]  
**Duration**: [minutes]

## Wins Celebrated

- [Accomplishment we recognized]
- [Growth or contribution we acknowledged]

## Challenges Discussed

- [Blocker and discussion]
- [Support or resource needed]

## Action Items

- [ ] [Commitment from manager] — Due: [date]
- [ ] [Commitment from team member] — Due: [date]

## Growth & Development

- **Career Goal**: [aspiration they shared or we discussed]
- **Learning Need**: [skill or knowledge to develop]
- **Stretch Assignment**: [opportunity for growth]

## Feedback

- **Strength**: [specific feedback on what they do well]
- **Growth Area**: [constructive feedback on development]

## Next Topics

- [Topic for next 1:1]
- [Follow-up on [topic]]

---
[[team/<name-slug>]] | [[meetings]]
```
