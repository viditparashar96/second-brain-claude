---
name: ops-sop-creator
description: Creates and maintains Standard Operating Procedures with version history and team ownership
argument-hint: "[create|update|list] [process-name] [optional-steps]"
triggers:
  - "create SOP"
  - "write SOP"
  - "document process"
  - "standard operating procedure"
  - "procedure for"
  - "how we do"
  - "update SOP"
  - "SOP template"
---

# SOP Creator

Create and maintain Standard Operating Procedures that document processes, define roles, and ensure consistency across the organization. Generates structured SOPs with decision points, exception handling, and review schedules.

## When to Trigger

- User needs to document a repeatable business process
- Process has been done multiple times inconsistently and needs standardization
- New team member onboarding requires process documentation
- Process owner needs to create or update SOP for review/audit
- User says "create SOP for [process]" or "document how we [action]"
- Process audit identifies need for new or revised SOP

## Workflow

1. **Extract parameters** — Parse from user input:
   - Process name (slug-friendly)
   - Process owner/department
   - Steps or description of the current process
   - Review frequency (monthly, quarterly, annually)
   - Optional: who can approve, dependencies, critical timeline

2. **Check product context** — From PRODUCTS.md (already in session context), identify if the process relates to a specific product. If so, pull the product's tech stack, known issues, and deployment context for accurate SOP documentation.

3. **Search vault for related processes** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<process-name> process procedure" --top-k 5
   ```
   Find related SOPs, process documentation, team notes to ensure consistency

4. **Check for team/owner context** — Run:
   ```bash
   cat ~/.second-brain/vault/team/*.md | grep -i "<process-owner>"
   ```
   Extract owner role, responsibilities, dependencies

5. **Search daily log for process issues** — Run:
   ```bash
   grep -r "<process-name>\|bottleneck\|delay\|exception" ~/.second-brain/vault/daily/ | tail -20
   ```
   Identify pain points, exceptions, or inefficiencies from past notes

6. **Generate structured SOP** with sections:
   - **Purpose** — Why this process exists, business value (2-3 sentences)
   - **Scope** — When and where this process applies, who it affects, prerequisites
   - **Roles & Responsibilities** — Key roles (owner, approver, executor) and their accountabilities
   - **Prerequisites** — Information, access, or approvals needed before starting
   - **Step-by-Step Procedure** — Numbered steps (typically 8-15 steps):
     - Clear, action-oriented language
     - Include decision points ("If X, then do Y")
     - Mention tools/systems required
     - Estimated time for each step
   - **Exception Handling** — What to do if steps fail or exceptions occur
   - **Tools & Access Required** — Systems, software, or tools needed
   - **Sign-offs & Approvals** — Who approves completion, documentation requirements
   - **Review & Update Schedule** — How often reviewed, next review date
   - **Related SOPs** — Links to dependent processes using [[wiki-links]]

7. **Add YAML frontmatter**:
   ```yaml
   ---
   title: "[Process Name] SOP"
   process_owner: "[name/role]"
   version: "1.0"
   created_date: "[YYYY-MM-DD]"
   last_reviewed: "[YYYY-MM-DD]"
   next_review: "[YYYY-MM-DD]"
   status: "active"
   review_frequency: "quarterly"
   ---
   ```

8. **Save SOP** to:
   ```bash
   ~/.second-brain/vault/ops/sops/<process-slug>.md
   ```

9. **Create version history comment** in file footer:
   ```
   ## Version History
   - **v1.0** (YYYY-MM-DD) — Initial SOP created by [creator]
   ```

10. **Optionally create Asana task** for review/approval:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task \
     --project "Operations" \
     --name "Review & Approve SOP: [process-name]" \
     --assignee "[process-owner]" \
     --due-date "+7 days"
   ```

11. **Log to daily log**:
    ```bash
    - **HH:MM** — [OPS] SOP created: <process-name> (v1.0) — Owner: <owner>
    ```

## Rules

- SOP steps must be numbered and actionable (start with verb: "Review", "Approve", "Send", etc.)
- Include decision trees for complex logic (use "If... then..." statements)
- Keep language clear for non-experts; avoid jargon or explain technical terms
- Always include exception handling section — no process is perfect
- Never assume prior knowledge; define acronyms on first use
- Mark critical steps with ⚠️ warning if they impact product/customer
- Update version number in frontmatter when making changes (v1.0 → v1.1)
- Include estimated time for full process completion
- SOPs should be re-reviewed minimum annually (or per review_frequency)
- Use [[wiki-links]] to reference related processes, teams, and roles
- SOPs related to specific products must reference PRODUCTS.md for accurate tech stack and deployment context.

## Templates

Use this structure for SOP file:

```markdown
---
title: "[Process Name] SOP"
process_owner: "[Name/Role]"
version: "1.0"
created_date: "[YYYY-MM-DD]"
last_reviewed: "[YYYY-MM-DD]"
next_review: "[YYYY-MM-DD]"
status: "active"
review_frequency: "quarterly"
---

# [Process Name] Standard Operating Procedure

## Purpose

[Why does this process exist? What business value does it deliver? 2-3 sentences.]

## Scope

This SOP applies to [who/when/where]. It covers [what aspects]. Prerequisites: [what must be true before starting].

## Roles & Responsibilities

| Role | Responsibility |
|------|-----------------|
| Process Owner | [Owns, maintains, reviews SOP] |
| [Role 2] | [What they do] |
| [Role 3] | [What they do] |

## Prerequisites

Before starting this process, ensure:
- [Prerequisite 1]
- [Prerequisite 2]
- [Prerequisite 3]

## Procedure

**Estimated Duration**: [X minutes/hours]

1. **[Step title]** — [Action]. Use [tool/system]. Expected: [outcome]. Time: ~[mins].
2. **[Step title]** — [Action]. 
   - If [condition A], do [action A]
   - If [condition B], do [action B]
   - Time: ~[mins]
3. **[Continue for all steps]**

⚠️ **Critical Step** — [Mark important steps that affect customers or product]

## Exception Handling

| Exception | Cause | Action |
|-----------|-------|--------|
| [Issue] | [Why it happens] | [Steps to resolve] |
| [Issue] | [Why it happens] | [Steps to resolve] |

Escalation: If issues cannot be resolved at step X, contact [[team/owner]].

## Tools & Access Required

- [System/tool 1] — [What access/permissions needed]
- [System/tool 2] — [What access/permissions needed]

## Sign-offs & Approvals

- [Step X]: Requires approval from [role]
- [Step Y]: Requires documentation at [location]
- Final approval: [who signs off]

## Review & Update Schedule

**Review Frequency**: [Quarterly/Monthly/As-needed]
**Next Scheduled Review**: [YYYY-MM-DD]
**Last Reviewed**: [YYYY-MM-DD] by [who]

This SOP is reviewed [frequency]. To request updates, contact [[<process-owner>]].

## Related Processes

- [[ops/sops/related-process-1]]
- [[ops/sops/related-process-2]]

---

## Version History

- **v1.0** (YYYY-MM-DD) — Initial SOP created
- **v1.1** (YYYY-MM-DD) — [What changed]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
