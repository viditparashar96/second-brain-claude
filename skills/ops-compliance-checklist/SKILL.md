---
name: ops-compliance-checklist
description: Manage compliance requirements, run audits, and track remediation for audit readiness
argument-hint: "[check|create|status] [framework-name] [optional-focus-area]"
triggers:
  - "compliance check"
  - "run compliance audit"
  - "compliance status"
  - "audit checklist"
  - "compliance framework"
  - "compliance audit"
  - "are we compliant"
  - "compliance dashboard"
  - "compliance remediation"
---

# Compliance Checklist

Manage compliance requirements across regulatory frameworks (SOC 2, GDPR, HIPAA, ISO 27001, etc.). Run automated audits, track remediation, and generate compliance dashboards for audit readiness.

## When to Trigger

- User needs to audit compliance against a standard (SOC 2, GDPR, HIPAA, etc.)
- Compliance requirement needs to be documented and tracked
- Need overall compliance health status before audit or investor review
- User says "check compliance for [framework]" or "run compliance audit"
- Framework compliance status needs update
- Need to identify overdue or non-compliant items

## Workflow

1. **Extract parameters** — Parse from user input:
   - Command (check, create, status)
   - Framework name (SOC 2, GDPR, HIPAA, ISO 27001, CCPA, etc.)
   - Optional: specific domain/focus area (data security, access controls, etc.)

2. **For CREATE command** — Build new compliance framework:
   - Search vault for framework guidelines/templates:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<framework-name> requirements audit controls" --top-k 5
     ```
   - Search team docs for existing controls/policies:
     ```bash
     grep -r "policy\|control\|compliance" ~/.second-brain/vault/team/*.md
     ```
   - Create checklist with standard requirements for that framework

3. **For CHECK command** — Run compliance audit:
   - Load framework checklist:
     ```bash
     cat ~/.second-brain/vault/ops/compliance/<framework-slug>.md
     ```
   - For each requirement, verify status by:
     - Searching vault for evidence of implementation:
       ```bash
       grep -r "<requirement-keyword>" ~/.second-brain/vault/ops/*.md ~/.second-brain/vault/team/*.md
       ```
     - Checking related SOPs and procedures
     - Retrieving related documents and policies
   - Update status: compliant / non-compliant / in-progress / not-applicable
   - Document evidence location and owner

4. **For STATUS command** — Generate compliance dashboard:
   - Load all framework checklists:
     ```bash
     ls -la ~/.second-brain/vault/ops/compliance/*.md
     ```
   - Calculate metrics for each:
     - **Compliance Score** = (compliant items / total items) × 100%
     - **Critical Issues** = number of non-compliant critical controls
     - **In Progress** = remediation items in progress
     - **Overdue** = items past remediation deadline
   - Generate summary table with frameworks, scores, and action items

5. **Generate compliance checklist** with sections for each requirement:
   - **Requirement ID** (e.g., SOC 2 CC6.1)
   - **Control Name** — What this control does
   - **Status** — Compliant / Non-Compliant / In-Progress / Not-Applicable
   - **Evidence** — Document/location proving compliance
   - **Owner** — Who is responsible
   - **Last Verified** — Date of last audit
   - **Remediation Plan** — If non-compliant, what's the fix?
   - **Remediation Deadline** — When must it be fixed?
   - **Severity** — Critical / High / Medium / Low

6. **Save compliance framework** to:
   ```bash
   ~/.second-brain/vault/ops/compliance/<framework-slug>.md
   ```
   Include YAML frontmatter:
   ```yaml
   ---
   framework: "[Framework Name]"
   version: "[e.g., SOC 2 2022]"
   last_audited: "[YYYY-MM-DD]"
   next_audit: "[YYYY-MM-DD]"
   overall_status: "compliant|non-compliant|in-progress"
   compliance_score: "[X%]"
   ---
   ```

7. **Generate compliance dashboard** showing:
   ```
   COMPLIANCE DASHBOARD — [Date]
   
   [Framework Name] — [Score]%
   ├─ Compliant: [X] items ✓
   ├─ Non-Compliant: [X] items ✗ (CRITICAL: [X])
   ├─ In Progress: [X] items ◐
   └─ Overdue: [X] items ⚠️
   
   NEXT ACTIONS:
   - [Critical item] — Owner: [name] — Due: [date]
   - [High item] — Owner: [name] — Due: [date]
   ```

8. **Create Asana tasks for non-compliant items**:
   ```bash
   for each non-compliant item:
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task \
       --project "Compliance" \
       --name "Remediate [requirement]: [brief description]" \
       --assignee "[owner]" \
       --due-date "[remediation-deadline]" \
       --priority "critical" (if critical) or "high/normal"
   ```

9. **Add audit calendar events**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal create-event \
     --title "[Framework] Compliance Audit Due" \
     --date "[next-audit-date]" \
     --reminder "30 days before"
   ```

10. **Log to daily log**:
    ```bash
    - **HH:MM** — [OPS] Compliance audit: <framework-name> — Score: <score>% — Non-compliant: <count> critical
    ```

## Rules

- Critical controls must be compliant before ANY audit or investor review
- Mark requirements as "Critical" if they impact customer data, security, or legal liability
- Always document evidence location for each compliant item (helps auditors)
- Non-compliant items require owner assignment and remediation deadline
- Compliance Score = % of applicable items that are compliant (exclude "not-applicable")
- Audit frequency: minimum annually, or per regulatory requirement
- Keep historical compliance scores to track improvement trend
- Link remediation tasks to specific control requirements
- Use [[wiki-links]] to reference related policies, SOPs, and team owners
- Flag any compliance gap that could impact customer trust or regulatory standing

## Templates

Use this structure for compliance framework file:

```markdown
---
framework: "[Framework Name]"
version: "[Version, e.g., SOC 2 2022]"
scope: "[What this framework covers]"
last_audited: "[YYYY-MM-DD]"
next_audit: "[YYYY-MM-DD]"
audit_frequency: "annually|semi-annually|quarterly"
overall_status: "compliant|non-compliant|in-progress"
compliance_score: "[X%]"
auditor: "[Name/firm if applicable]"
---

# [Framework Name] Compliance Checklist

**Overall Status**: [Compliant/Non-Compliant/In-Progress]  
**Compliance Score**: [X%] ([Compliant items]/[Total applicable items])  
**Last Audited**: [YYYY-MM-DD]  
**Next Audit Due**: [YYYY-MM-DD]

---

## Compliance Summary

| Category | Compliant | Non-Compliant | In-Progress | Overdue | Score |
|----------|-----------|---------------|-------------|---------|-------|
| [Category 1] | [#] | [#] | [#] | [#] | [X%] |
| [Category 2] | [#] | [#] | [#] | [#] | [X%] |
| [Overall] | [#] | [#] | [#] | [#] | [X%] |

---

## Critical Issues (Must Remediate)

⚠️ **[Count] CRITICAL non-compliant items require immediate remediation**

| Requirement | Control | Owner | Deadline | Action |
|-------------|---------|-------|----------|--------|
| [ID] | [Name] | [Owner] | [Date] | [Link to Asana task] |

---

## Control Requirements

### [Category Name]

#### [Control ID]: [Control Name]

**Requirement**: [What must be true for compliance]

**Severity**: Critical / High / Medium / Low

**Current Status**: 
- ✓ Compliant
- ◐ In-Progress
- ✗ Non-Compliant
- — Not Applicable

**Evidence of Compliance** (if compliant):
- Document: [Link to policy/evidence]
- Location: [Where this is documented]
- Last Verified: [YYYY-MM-DD]

**Evidence Owner**: [Team member responsible]

**Remediation Plan** (if non-compliant):
- Issue: [What is not compliant]
- Root Cause: [Why]
- Remediation Steps: [How to fix]
- Owner: [Who is fixing it]
- Deadline: [YYYY-MM-DD]
- Related Asana Task: [Link]

**Notes**: [Any context or exceptions]

---

[Continue for all control requirements...]

---

## Non-Compliant Items Summary

**Total Non-Compliant**: [X] items  
**Critical**: [X] | **High**: [X] | **Medium**: [X] | **Low**: [X]

### Overdue Remediations

| Control | Owner | Original Deadline | Days Overdue | Status |
|---------|-------|------------------|--------------|--------|
| [ID] | [Owner] | [Date] | [X] | Escalate |

### In-Progress Remediations

| Control | Owner | Target Completion | % Complete | Notes |
|---------|-------|------------------|------------|-------|
| [ID] | [Owner] | [Date] | [%] | [Status] |

---

## Audit Trail

| Date | Action | Notes | Auditor |
|------|--------|-------|---------|
| [YYYY-MM-DD] | [Audit/Update] | [Summary] | [Name] |
| [YYYY-MM-DD] | [Remediation completed] | [What was fixed] | [Name] |

---

## Related Documentation

- [[ops/sops/security-policy]]
- [[ops/sops/access-control]]
- [[team/security-team]]
- External: [Link to auditor report, if external audit]

---

Last Updated: [YYYY-MM-DD] by [Name]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
