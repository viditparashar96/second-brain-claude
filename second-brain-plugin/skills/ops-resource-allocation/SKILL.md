---
name: ops-resource-allocation
description: Track and optimize team resource allocation across projects and identify skill gaps
argument-hint: "[view|plan|gaps] [optional-team|period]"
triggers:
  - "resource allocation"
  - "team capacity"
  - "resource plan"
  - "who is available"
  - "allocation matrix"
  - "capacity planning"
  - "skill gaps"
  - "team overload"
  - "resource optimization"
---

# Resource Allocation

Track team member allocation across projects, identify over/under-utilized resources, and surface skill gaps for upcoming work. Generates allocation matrices and capacity planning reports.

## When to Trigger

- Planning resource assignment for new projects/initiatives
- Need to see current team capacity and utilization
- Want to identify overloaded team members or skill gaps
- Need capacity forecast for upcoming work
- Resolving conflicts when team member assigned to multiple projects
- User says "plan resources for [project]" or "who's available for [work]"

## Workflow

1. **Extract parameters** — Parse from user input:
   - Command (view, plan, gaps)
   - Optional: team/department filter
   - Optional: time period (current week, next month, quarter)

2. **For VIEW command** — Generate current allocation snapshot:
   - Fetch all Asana tasks assigned to team members:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana list-tasks \
       --filter "assignee-team=[team-name]" --max 500
     ```
     Extract: assigned team member, project, task, due date, estimated effort
   
   - Fetch calendar events for team (meetings, blocked time):
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal list-events \
       --attendee "[team-email-list]" --days-ahead 30
     ```
     Calculate meeting load per person
   
   - Load team roles and capacity from vault:
     ```bash
     cat ~/.second-brain/vault/team/*.md
     ```
     Extract: role, department, capacity (hours/week available), skills, seniority

3. **For PLAN command** — Plan allocation for upcoming work:
   - List upcoming projects/initiatives:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "project pipeline upcoming initiative" --top-k 10
     ```
   - For each project, estimate resource needs (engineering hours, design, QA, etc.)
   - Match available team members to requirements
   - Identify conflicts (same person needed on overlapping projects)
   - Generate allocation plan with assignments and timelines

4. **For GAPS command** — Identify skill/capacity gaps:
   - Analyze upcoming projects vs. available skills:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "needed skills project requirements" --top-k 5
     ```
   - Compare to current team skills (from team/ vault files)
   - Identify:
     - Skills not present on team (hiring gaps)
     - Overloaded roles (need to hire more of this skill)
     - Underutilized resources
     - Single-points-of-failure (only one person with critical skill)

5. **Build allocation matrix** — Team member × Project/Work:
   ```
   | Team Member | Role | Current Allocation | Capacity Remaining | % Utilized |
   |-------------|------|-------------------|-------------------|-----------|
   | [Name] | [Role] | [Current tasks] | [X hours/week] | [Y%] |
   ```

6. **Generate allocation report** with sections:
   - **Current Allocation Summary**:
     - Total team capacity (hours/week available)
     - Total allocated (hours/week assigned)
     - Utilization % (allocated / available)
     - Available capacity remaining
   
   - **Allocation by Team Member**:
     | Name | Role | % Utilized | Projects | Blocker? |
     |------|------|-----------|----------|----------|
     | [Name] | [Role] | [X%] | [Project 1, Project 2] | [Overloaded/Underutilized/Optimal] |
   
   - **Over-Allocated Team Members** (>100% utilization):
     - Who: [Name] — [X% allocated]
     - Current projects: [list]
     - What to do: reduce scope, add resources, extend timeline
   
   - **Under-Allocated Resources** (<50% utilization):
     - Who: [Name] — [X% allocated]
     - Could take on: [X additional hours/week]
     - Opportunities: [what work could they help with]
   
   - **Skills Assessment**:
     - Skills on team: [list with # of people]
     - Skills gaps for upcoming work: [list what's missing]
     - Single-point-of-failure risks: [people with critical unique skills]
   
   - **Project Resource Needs vs. Supply**:
     | Project | Timeline | Needs | Available | Gap | Risk |
     |---------|----------|-------|-----------|-----|------|
     | [Project] | [Dates] | [4 eng, 1 design] | [3 eng, 1 design] | [1 eng] | High |

7. **Identify conflicts and recommendations**:
   - **Conflicts**: [Person A needed on Project 1 and Project 2 simultaneously]
     - Recommendation: [prioritize, split effort, hire, or delay]
   - **Overload**: [Person B at 150% allocation]
     - Recommendation: [move work to Person C, hire contractor, reduce scope]
   - **Underutilization**: [Person C at 30% allocated]
     - Recommendation: [assign to Project X, grow skills in Y, develop new capability]

8. **Save allocation snapshot** to:
   ```bash
   ~/.second-brain/vault/ops/allocation/YYYY-MM-DD-allocation.md
   ```
   Include YAML frontmatter:
   ```yaml
   ---
   date: "[YYYY-MM-DD]"
   period: "[current|[start-date] to [end-date]]"
   total_capacity_hours: "[X hours/week]"
   total_allocated_hours: "[X hours/week]"
   utilization_percent: "[X%]"
   ---
   ```

9. **Create Asana tasks for resource actions**:
   - For over-allocated: create task to prioritize/rescope
   - For skill gaps: create hiring or training task
   - For underutilized: create assignment task or skill-building project
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task \
     --project "Operations" \
     --name "[Resource action]: [brief description]" \
     --assignee "[manager]" \
     --due-date "[action-date]"
   ```

10. **Add capacity review to calendar** (monthly or quarterly):
    ```bash
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal create-event \
      --title "Team Capacity Review & Resource Planning" \
      --date "[monthly/quarterly]" \
      --recurring "[monthly|quarterly]"
    ```

11. **Log to daily log**:
    ```bash
    - **HH:MM** — [OPS] Resource allocation snapshot: <team-name> — Utilization: <percent>% — Gaps: <count> critical
    ```

## Rules

- Utilization should target 70-85% (leaves buffer for unexpected work, learning, sick time)
- Over 100% allocation signals overload — escalate to management immediately
- Under 30% utilization suggests available capacity or potential alignment issue
- Skills assessment must identify mission-critical skills (who would we lose sleep over losing?)
- Account for meetings, admin work, and context-switching overhead (typically 10-20% of capacity)
- Resource conflicts should be resolved by prioritization, not by overloading people
- Always include lead time for hiring/training when forecasting resource needs
- Link resource plans to [[projects/]] and [[team/]] vault files
- Review allocation monthly with team leads; update forecast quarterly

## Templates

Use this structure for allocation snapshot file:

```markdown
---
date: "[YYYY-MM-DD]"
period: "[current week | YYYY-MM through YYYY-MM | YYYY-QX]"
total_capacity_hours: "[X hours/week]"
total_allocated_hours: "[X hours/week]"
utilization_percent: "[X%]"
status: "optimal|high-utilization|skills-gap|need-hiring"
---

# Resource Allocation Snapshot

**As of**: [YYYY-MM-DD]  
**Period**: [Period covered]  
**Team**: [[team/<team-name>]]  
**Prepared by**: [Name]

---

## Allocation Summary

**Total Team Capacity**: [X hours/week] ([Y team members])  
**Total Allocated**: [X hours/week]  
**Utilization Rate**: [X%]  
**Available Capacity**: [X hours/week]

**Status**: [Optimal (70-85%) | High Utilization (>85%) | Underutilized (<50%)]

---

## Team Member Allocation

| # | Name | Role | Capacity | Allocated | Utilized | Projects | Status |
|---|------|------|----------|-----------|----------|----------|--------|
| 1 | [Name] | [Role] | [X hrs/wk] | [X hrs/wk] | [X%] | [Project A, Project B] | [Optimal/Overloaded/Underutilized] |
| 2 | [Name] | [Role] | [X hrs/wk] | [X hrs/wk] | [X%] | [Project C] | [Status] |
| — | **TOTAL** | — | [X] | [X] | [X%] | — | — |

**Legend**: ✓ Optimal (70-85%) | ⚠️ High (>85%) | ◐ Available (<50%)

---

## Over-Allocated Team Members

⚠️ **[Count] team members over 100% allocation** — Immediate action needed

| Name | Role | Utilization | Projects | Effort (est. hrs/wk) | Recommendation |
|------|------|-------------|----------|---------------------|-----------------|
| [Name] | [Role] | [X%] | [Project A, Project B] | [X hrs] | Reduce scope on [Project], add resource, extend timeline |
| [Name] | [Role] | [X%] | [Project C, Project D] | [X hrs] | [Recommendation] |

**Actions Required**:
- [ ] Meet with [manager] to prioritize/rescope
- [ ] Assign Asana task: [link]
- [ ] Decision by: [YYYY-MM-DD]

---

## Under-Allocated Resources

✓ **[Count] team members with available capacity**

| Name | Role | Utilization | Capacity Remaining | Opportunity | Notes |
|------|------|-------------|-------------------|-------------|-------|
| [Name] | [Role] | [X%] | [X hrs/week] | Assign to [Project], train in [skill] | [Context] |
| [Name] | [Role] | [X%] | [X hrs/week] | [Opportunity] | [Context] |

**Options**:
- Assign to high-priority project work
- Skill development in [area]
- Cross-training on [[team/<other-team>]]

---

## Upcoming Projects — Resource Forecast

**Next [3 months | Quarter]**

| Project | Timeline | Phase | Needed | Available | Gap | Status |
|---------|----------|-------|--------|-----------|-----|--------|
| [Project A] | [Start-End] | [Phase] | [4 eng, 1 design, 2 qa] | [3 eng, 1 design, 2 qa] | [1 eng needed] | At Risk |
| [Project B] | [Start-End] | [Phase] | [2 eng, 1 PM] | [2 eng, 0 PM] | [1 PM, hire or contract] | Needs PM |
| [Project C] | [Start-End] | [Phase] | [1 design] | [1 design available from [Name]] | [None] | Covered |

---

## Skills Assessment

**Skills on Team** (Current):

| Skill | # of People | Seniority | Risk Level | Notes |
|-------|-------------|-----------|-----------|-------|
| [Skill: Python] | 3 | 2 senior, 1 junior | Low | Adequate coverage |
| [Skill: DevOps] | 1 | Senior | **HIGH** | [Name] is single point of failure |
| [Skill: Product Design] | 1 | Senior | **HIGH** | [Name] only designer |
| [Skill: Data Analytics] | 0 | — | **CRITICAL** | Not on team — needed for [Project] |

**Skills Gap for Upcoming Work**:

| Skill | Projects Needing | Current Supply | Gap | Action |
|-------|-----------------|-----------------|-----|--------|
| [Machine Learning] | [Project A, Project B] | 0 | Critical | Hire ML engineer by [date] |
| [Kubernetes] | [Project C] | 1 (junior) | 1 senior needed | Train [Name] or hire |
| [GraphQL] | [Project D] | 0 | 1 developer | Contract resource or hire |

**Critical Single Points of Failure**:
- **[[Name]]** — Only person with [DevOps/Production Support/Architecture] skills
  - Risk: If unavailable, [Project/capability] is blocked
  - Mitigation: Cross-train [[other-name]], document critical processes, hire backup

---

## Resource Planning Recommendations

### Priority 1 (Immediate)

- **Action**: Resolve overallocation of [[Name]] 
  - Options: [Reduce [Project] scope | Extend timeline | Add contractor]
  - Decision needed by: [YYYY-MM-DD]
  - Owner: [[manager]]

- **Action**: Address critical skill gap in [Skill]
  - Options: [Hire | Contract | Train [Name]]
  - Timeline: [By YYYY-MM-DD]
  - Owner: [[manager]]

### Priority 2 (Next Month)

- **Action**: [Assign available capacity from [Name] to [Project]]
- **Action**: [Plan skill development for [Name] in [area]]
- **Action**: [Cross-train [person] on [critical skill] to reduce single-point-of-failure risk]

### Priority 3 (This Quarter)

- **Action**: [Explore hiring or contracting for [skill gap]]
- **Action**: [Plan resource allocation for [future project]]

---

## Capacity Planning Assumptions

- **Available hours/week per person**: [X hours] (accounting for [meetings, admin, overhead])
- **Project buffers**: [X%] buffer for unexpected work
- **Ramp-up time**: New hires need [X weeks] to be fully productive
- **Context-switching overhead**: [X%] estimated loss from task-switching

---

## Next Steps

1. **Review** — Share allocation snapshot with [[team/<managers>]]
2. **Discuss** — Address over-allocated team members and skill gaps
3. **Plan** — Create action items for hiring, training, or rescoping
4. **Monitor** — Update allocation monthly; reassess quarterly
5. **Follow-up** — Calendar reminder for next allocation review: [YYYY-MM-DD]

---

## Related Documentation

- [[team/<team-name>]]
- [[projects/current-initiatives]]
- [[ops/hiring-plan]]

---

**Report Generated**: [YYYY-MM-DD] by [Name]  
**Next Allocation Review**: [YYYY-MM-DD]
```
