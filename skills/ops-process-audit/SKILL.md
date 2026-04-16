---
name: ops-process-audit
description: Audit existing processes for bottlenecks, inefficiencies, and improvement opportunities
argument-hint: "[process-name|area] [optional-focus-area]"
triggers:
  - "audit process"
  - "process improvement"
  - "process analysis"
  - "bottleneck analysis"
  - "how can we improve"
  - "efficiency review"
  - "process inefficiency"
  - "workflow audit"
  - "process review"
---

# Process Audit

Analyze existing operational processes to identify bottlenecks, inefficiencies, and improvement opportunities. Generates comprehensive audit reports with recommendations and implementation priorities.

## When to Trigger

- User wants to improve an existing process for speed/efficiency/quality
- Process has recurring complaints or escalations
- Team reports bottlenecks or delays in a workflow
- User says "audit [process]" or "how can we improve [area]"
- Performance metrics show process is slowing down operations
- Cost or quality issues traced back to a process

## Workflow

1. **Extract parameters** — Parse from user input:
   - Process name or operational area (e.g., "customer onboarding", "bug triage", "hiring")
   - Optional: specific focus area (speed, quality, cost, compliance)

2. **Search vault for related SOPs** — Get current documented process:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<process-name> SOP procedure steps" --top-k 3
   ```
   If found, load the SOP:
   ```bash
   cat ~/.second-brain/vault/ops/sops/<process-slug>.md
   ```

3. **Search vault for process context** — Find references and issues:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<process-name> bottleneck issue problem delay" --top-k 10
   ```
   Review meeting notes, team docs, project retrospectives mentioning this process

4. **Search daily log for pain points** — Identify recurring complaints:
   ```bash
   grep -r "<process-name>\|bottleneck\|delay\|waiting\|stuck\|manual\|repetitive" ~/.second-brain/vault/daily/ | tail -50
   ```
   Extract: when complaints happen, who's affected, impact severity

5. **Search Gmail for complaints/escalations** — Find process issues reported:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "subject:(urgent|escalation|issue|problem|delay) <process-area>" --max 30
   ```
   Extract: complaint details, who complained, frequency, resolution

6. **Analyze current process** — Document:
   - **Current State** — Steps as currently performed (may differ from documented SOP)
   - **Actors** — Who is involved at each step
   - **Bottlenecks** — Where delays occur:
     - Manual handoffs between teams
     - Waiting for approvals or decisions
     - Rework or quality issues requiring iteration
     - Dependency on unavailable person/system
   - **Cycle Time** — How long does full process take? Theoretical vs. actual?
   - **Cost** — How much does this process cost to run? (labor, tools, opportunity cost)
   - **Pain Points** — From email/daily log analysis, what goes wrong most often?

7. **Calculate efficiency metrics**:
   - **Value-Add Time** = time spent on actual productive work
   - **Non-Value-Add Time** = waiting, rework, handoffs, approvals
   - **Efficiency Ratio** = (Value-Add / Total Time) × 100%
   - **Bottleneck Impact** = % of total cycle time spent at biggest bottleneck
   - **Error Rate** = % of processes requiring rework/iteration (if available from data)

8. **Identify improvement opportunities**:
   - Can steps be combined or parallelized?
   - Can automation replace manual work? (RPA, workflow tool, etc.)
   - Are approvals/reviews necessary or just habit?
   - Can bottleneck be eliminated (different owner, better tooling, etc.)?
   - What would cut cycle time in half?

9. **Generate audit report** with sections:
   - **Executive Summary** — Current state, main bottleneck, recommended fix, estimated impact
   - **Process Overview** — Current documented process (link to SOP if exists)
   - **Current Performance Metrics**:
     - Cycle time (baseline to target)
     - Efficiency ratio (value-add vs. non-value-add)
     - Error/rework rate
     - Cost to run process
   - **Bottlenecks Identified** — Ranked by impact:
     - Bottleneck name, location in process, time lost, root cause
     - How often does this create problems?
   - **Process Issues from History**:
     - Complaints/escalations from emails and daily log
     - Recurring problems with pattern of occurrence
   - **Improvement Recommendations** — 3-5 prioritized recommendations:
     - What to change and why
     - Expected impact (time saved, cost, quality improvement)
     - Implementation effort and timeline
     - Owner/responsible team
     - Related tools/resources needed
   - **Implementation Plan** — Detailed steps for top 1-2 recommendations
   - **Success Metrics** — How to measure improvement once implemented

10. **Save audit report** to:
    ```bash
    ~/.second-brain/vault/ops/audits/YYYY-MM-DD-<process-slug>-audit.md
    ```

11. **Create Asana tasks** for improvement actions:
    ```bash
    for each recommendation:
      python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task \
        --project "Operations" \
        --name "[Recommendation]: [brief description]" \
        --assignee "[owner]" \
        --due-date "[implementation-date]" \
        --description "[details and expected impact]"
    ```

12. **Optionally create meeting event** for process improvement kickoff:
    ```bash
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal create-event \
      --title "Process Audit Review: [process-name]" \
      --date "+3 days" \
      --attendees "[stakeholders]"
    ```

13. **Log to daily log**:
    ```bash
    - **HH:MM** — [OPS] Process audit: <process-name> — Main bottleneck: <bottleneck> — Top recommendation: <rec> (est. <impact>)
    ```

## Rules

- Always compare documented SOP vs. how process actually runs (they often differ)
- Bottlenecks are often human (waiting for a person, approval delays) not technical
- Don't just optimize speed — consider quality, compliance, and cost together
- Recommendations should include effort estimate and ROI (time/cost saved vs. implementation effort)
- If process affects customer experience, prioritize customer-visible improvements
- Link audit report to related SOPs using [[wiki-links]]
- Document source of complaints/issues (email, daily log) to back up findings
- Implementation priority should consider: impact, effort, and strategic alignment
- Follow up on implemented improvements to measure actual vs. predicted impact

## Templates

Use this structure for audit report file:

```markdown
---
title: "[Process Name] Audit Report"
process_name: "[Name]"
audit_date: "[YYYY-MM-DD]"
auditor: "[Name/team]"
status: "completed|in-progress"
overall_recommendation: "optimize|restructure|automate|retire"
---

# [Process Name] Audit Report

**Audit Date**: [YYYY-MM-DD]  
**Process Owner**: [[team/owner]]  
**Auditor**: [Name]  
**Scope**: [What this audit covers]

---

## Executive Summary

**Current State**: [1-2 sentence description of how process works today]

**Main Problem**: [The biggest bottleneck/inefficiency identified]

**Recommended Action**: [Top recommendation for improvement]

**Expected Impact**: [Time/cost/quality improvement expected if recommendation implemented]

**Implementation Effort**: [Estimated weeks/months and resources needed]

**Business Case**: [Reason this is worth doing — customer impact, cost savings, quality, etc.]

---

## Process Overview

**Current Documented Process**: [[ops/sops/<process-name>]] (v[X])

**Process Objective**: [What this process is supposed to accomplish]

**Stakeholders**: [Teams/people involved]

**Frequency**: [How often does this process run? Daily? Per-request?]

**Current Owners**: [[team/<owner>]]

---

## Current Performance Metrics

| Metric | Baseline | Target | Status | Notes |
|--------|----------|--------|--------|-------|
| Cycle Time | [X hours/days] | [X hours/days] | [△%] | From start to finish |
| Efficiency Ratio | [X%] | [80%+] | [△%] | Value-add time vs. total time |
| Rework/Error Rate | [X%] | [<5%] | [△%] | % requiring iteration |
| Cost Per Process | $[X] | $[target] | [△%] | Labor + tools |
| Customer Satisfaction | [score] | [target] | [△] | If customer-facing |

**Efficiency Analysis**:
- Value-Add Time: [X minutes] (productive work on deliverable)
- Non-Value-Add Time: [X minutes] (waiting, handoffs, rework, approvals)
- Bottleneck Time: [X minutes] at [[step-name]]

---

## Bottlenecks Identified

### Bottleneck #1: [Name] — **High Impact**

**Location in Process**: Step [X] — [description]

**Time Lost**: [X minutes] per process run ([Y%] of total cycle time)

**Frequency**: [How often is this a problem? Every time? Sometimes?]

**Root Cause**: 
- [Primary cause]
- [Secondary cause]

**Impact**: 
- Delays downstream tasks
- Causes [customer/team] frustration
- Cascades to [[related-process]]

**Example**: [Specific instance from email/daily log showing this bottleneck]

### Bottleneck #2: [Name] — **Medium Impact**

[Same structure...]

---

## Issues & Complaints from History

**Data Sources**: Gmail ([X] complaints over past 6 months) + Daily Log ([X] mentions)

| Date | Issue | Reporter | Impact | Root Cause |
|------|-------|----------|--------|-----------|
| [YYYY-MM-DD] | [Complaint] | [Who] | [Customer/team impact] | Related to [[bottleneck-1]] |
| [YYYY-MM-DD] | [Complaint] | [Who] | [Impact] | Related to [[bottleneck-2]] |

**Pattern**: [What recurring issues emerge? Who is most affected?]

---

## Improvement Recommendations

Ranked by **Impact × Feasibility** score.

### Recommendation #1: [Improvement Idea] — **Priority: High**

**What to Change**: [Clear description of the change]

**Why This Helps**: 
- Eliminates bottleneck: [[bottleneck-1]]
- Reduces cycle time by [X%]
- Improves quality by [metric]

**Expected Impact**:
- **Time Savings**: [X hours/days per process] → $[annual savings if labor-intensive]
- **Quality**: [% reduction in rework]
- **Customer Impact**: [Better experience, faster delivery, etc.]

**Implementation Approach**:
- [Step 1: Do X]
- [Step 2: Do Y]
- [Step 3: Train team / rollout]

**Resources Needed**:
- [Tool/software investment: $X]
- [Labor: X person-days]
- [Training: X hours]

**Timeline**: [X weeks] from approval to full deployment

**Owner**: [[team/<owner>]]

**Success Metrics**:
- New cycle time: [X hours/days]
- New efficiency ratio: [X%]
- Error rate: <[X%]

---

### Recommendation #2: [Improvement Idea] — **Priority: Medium**

[Same structure...]

---

### Recommendation #3: [Improvement Idea] — **Priority: Low**

[Same structure...]

---

## Implementation Roadmap

**Phase 1 (Weeks 1-2)**: 
- [Implement recommendation #1]
- Owner: [[<owner>]]
- Asana Task: [Link]

**Phase 2 (Weeks 3-6)**:
- [Implement recommendation #2]
- Owner: [[<owner>]]
- Asana Task: [Link]

**Phase 3 (Ongoing)**:
- [Monitor and measure results]
- [Make adjustments based on feedback]

---

## Related Processes & Dependencies

- [[ops/sops/<related-process-1>]]
- [[ops/sops/<related-process-2>]]
- [[ops/vendors/<relevant-vendor>]] (if tool-dependent)

---

## Next Steps

1. **Review** — Present audit findings to [[team/<owner>]] and stakeholders
2. **Decide** — Approve/defer/reject each recommendation
3. **Plan** — Schedule implementation kickoff for approved recommendations
4. **Execute** — Assign owners and track progress in Asana
5. **Measure** — Track new metrics post-implementation (set calendar reminder for [YYYY-MM-DD])

---

**Audit Conducted By**: [Name]  
**Date**: [YYYY-MM-DD]  
**Next Review**: [YYYY-MM-DD + 90 days]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
