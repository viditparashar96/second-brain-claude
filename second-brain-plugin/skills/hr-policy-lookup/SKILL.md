---
name: hr-policy-lookup
description: Search company policies and answer HR questions — or help draft new policies
argument-hint: "[HR question or policy topic]"
triggers:
  - "company policy"
  - "HR question"
  - "handbook lookup"
  - "what's the policy"
  - "draft policy"
  - "employee handbook"
---

# Policy Lookup

Search company policies and handbooks in the vault to answer HR questions. Cites specific policy documents. Can also help draft new policies if they don't exist.

## When to Trigger

- Employee or manager asks an HR policy question ("What's the PTO policy?", "Can employees work remote?")
- HR team needs to draft or update a policy
- Legal or compliance review needed
- New policy discussion or implementation
- Someone says "handbook", "policy", "employee agreement", or asks "What's the company...?"

## Workflow

### Step 1: Identify the Question

Ask or extract the policy question:

- "What is your question or policy topic?"
- If they paste a situation, clarify: "Are you asking about remote work policy? Expense reimbursement?"

### Step 2: Search Vault Policies

Search for relevant policies:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{policy_topic}" --top-k 5 --path-prefix "hr/policies"
```

Also search broader research/handbook area:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{topic}" --top-k 5 --path-prefix "research"
```

Examples:
- Question: "Can I work from home?" → Search: "remote work policy"
- Question: "How much PTO do I get?" → Search: "pto leave vacation policy"
- Question: "What's the code of conduct?" → Search: "code of conduct ethics"

### Step 3: Evaluate Results

**If policy document found:**
1. Read the relevant policy file
2. Extract the specific answer to their question
3. Cite the policy document and section

**If policy not found:**
1. Say clearly: "I didn't find a policy on this in our handbook. Let me check if we need to draft one."
2. Ask: "Should I help draft this policy? If so, let me know the details."

### Step 4: Answer with Citations

Respond with:

```markdown
**Question:** {Their question}

**Answer:** {Clear, direct answer with specific policy details}

**Policy Reference:** [[hr/policies/{policy-filename}]] — Section "{Section Name}"

**Key Points:**
- {Key point 1}
- {Key point 2}
- {Key point 3}

**Questions or disputes?** This represents the current policy. Contact [[team/HR-contact-name]] for clarification.
```

### Step 5: Handle Policy Gaps

If no policy exists:

```markdown
**Question:** {Question}

**Answer:** No current policy found on this topic.

**Options:**
1. I can help draft a policy for this. Details I'd need: {relevant factors}
2. Talk to HR/leadership to decide company stance
3. Create a temporary exception and document it

**Draft Policy Template:** (if requested)
```

Then ask:
- "What's the company's intended stance on this? (required context to draft)"
- "Who should approve it?"
- "Should I create a draft and save it to the vault?"

### Step 6: Draft New Policy (If Requested)

If they approve drafting a new policy:

Create file at `~/.second-brain/vault/hr/policies/{topic-slug}.md`:

```markdown
# {Policy Title}

**Effective Date:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Owner:** {Department or Role}
**Status:** Draft | Approved | In Review

---

## Purpose

{Why this policy exists and what it covers}

---

## Scope

{Who this applies to — all employees, certain departments, contractors, etc.}

---

## Policy

### {Section 1}

{Details, rules, procedures, examples}

### {Section 2}

{Details}

---

## Examples

### ✓ Acceptable

{Example 1 that follows policy}

{Example 2}

### ✗ Not Acceptable

{Example 1 that violates policy}

{Example 2}

---

## Process / How to Request

{Step-by-step: how does someone invoke this policy? Who approves? What's the timeline?}

---

## FAQ

**Q: {Common question}**  
A: {Answer}

**Q: {Common question}**  
A: {Answer}

---

## Related Policies

- [[hr/policies/{related-policy}]]
- [[hr/policies/{related-policy}]]

---

## Contact

Questions about this policy? Reach out to [[team/{policy-owner}]] or email hr@company.com

---

## Revision History

| Date | Version | Change |
|------|---------|--------|
| YYYY-MM-DD | 1.0 | Initial policy |
```

Save to vault and mark as "Draft" or "In Review" depending on approval status.

### Step 7: Log Query

Append to daily log:

```
- **HH:MM** — Policy lookup: "{question}" → [Found / Not found / Draft started]
```

Track for analytics: common questions might mean gaps or confusion in communication.

## Common Policy Templates

### Remote Work Policy

```markdown
# Remote Work Policy

**Scope:** All full-time employees

**Framework:**
- **Fully Remote:** Roles approved for 100% remote work (list specific roles)
- **Hybrid:** 2 days/week in office, 3 days/week flexible
- **In-Office:** Role requires daily in-office presence (field, client-facing, etc.)

**Requirements:**
- Reliable internet (upload 10 Mbps, download 25 Mbps)
- Quiet workspace
- Core hours: 10am-3pm in timezone
- Attend in-person team days / monthly all-hands

**Manager Approval:** Yes, case-by-case
```

### PTO / Vacation Policy

```markdown
# Time Off Policy

**Annual Allocation:**
- {Years 0-2}: {N} days
- {Years 2-5}: {N} days
- {Years 5+}: {N} days

**Types:**
- Paid Time Off (PTO) — flexible use
- Sick Days — illness, medical appointments
- Holidays — {list company holidays}
- Parental Leave — {N} weeks
- Sabbatical — {if applicable}

**Process:**
1. Request in {system} (Asana, Calendar, HR system)
2. Manager approves
3. Notify team at least {N} weeks in advance
4. Update calendar as "Out of Office"
```

### Code of Conduct / Values

```markdown
# Code of Conduct

**Our Values:**
1. Respect — Treat others with dignity
2. Integrity — Be honest and accountable
3. Inclusion — Welcome different perspectives
4. Excellence — Deliver quality work

**Expectations:**
- No harassment, discrimination, or bullying
- Professional communication
- Confidentiality of company/client data
- No conflicts of interest without disclosure
```

## Rules

- **Never make up policies** — If it doesn't exist in the vault, say so clearly
- **Cite sources** — Always link to the specific policy document
- **Unclear policies** — If a policy is ambiguous, note that and suggest it be clarified
- **Drafts are suggestions** — New policy drafts must be reviewed and approved by management before going into effect
- **Policy changes** — If a policy is updated, keep a revision history and notify relevant teams
- **Legal review** — For sensitive policies (discrimination, leave, harassment), recommend legal review before finalizing
- **Consistency** — Check existing policies before drafting new ones to avoid contradictions
- **Regular audit** — Recommend HR periodically review all policies for currency and accuracy
