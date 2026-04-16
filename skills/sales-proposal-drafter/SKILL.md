---
name: sales-proposal-drafter
description: Draft client proposals using vault context and templates with tone matching
argument-hint: "[client-name] [scope] [deliverables] [timeline] [optional-pricing]"
triggers:
  - "draft proposal"
  - "write proposal"
  - "proposal for"
  - "create proposal"
  - "proposal template"
  - "proposal needed"
---

# Proposal Drafter

Draft professional client proposals using vault context, past proposals for tone matching, and client history. Creates proposal documents ready for review and customization before sending.

## When to Trigger

- User needs to propose a project or engagement to a client
- Deal is qualified and ready to move into proposal stage
- User says "draft proposal for [client]" or "write proposal for [scope]"
- Follow-up after deal-prep call to formalize scope into proposal

## Workflow

1. **Extract parameters** — Parse from user input:
   - Client name
   - Project scope (what will be delivered)
   - Deliverables (list of outputs)
   - Timeline (project duration, milestones)
   - Pricing (if provided; if not, note as TBD)

2. **Load client context** — Run:
   ```bash
   cat ~/.second-brain/vault/clients/<client-slug>.md
   ```
   Extract: company, contact info, past engagements, relationship strength, budget awareness

3. **Pull product details** — From PRODUCTS.md (in session context), extract the relevant product's description, key features, pricing model, and competitive edge to include in the proposal.

4. **Search similar past proposals** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "proposal template scope deliverables" --top-k 3
   ```
   Find similar past proposals to match tone, structure, and language patterns

5. **Search past client emails** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<client-email>" --max 10
   ```
   Extract communication style, terminology they use, concerns they've raised

6. **Generate structured proposal** with sections:
   - **Executive Summary** — What you're proposing in 2-3 sentences, why it solves their problem
   - **About [Client]** — Show you understand their business and challenge (2-3 sentences)
   - **Proposed Scope** — What will be done, in plain language, 4-6 bullet points
   - **Deliverables** — Specific outputs (reports, code, designs, etc.) with dates
   - **Timeline** — Project phases/milestones with estimated duration
   - **Investment** — Total cost, payment terms, breakdown if relevant (or TBD if not decided)
   - **What's Included vs. Out of Scope** — Clear boundaries to prevent scope creep
   - **Next Steps** — How to move forward (review, sign, start date, etc.)
   - **Terms** — Standard terms, cancellation, change order process (brief reference to attached T&Cs)

7. **Match tone and style** — Use language from past emails and similar proposals to match your communication style with this client

8. **Save proposal** to:
   ```bash
   ~/.second-brain/vault/sales/proposals/YYYY-MM-DD-<client-slug>-proposal.md
   ```

9. **Optionally create Gmail draft** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail draft --to "<client-email>" --subject "Proposal: [project-name] for [client-name]" --body "<intro-email-text>"
   ```
   Draft email never sends — user reviews and clicks send manually

10. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] Proposal drafted: <client-name> — $<value> (<timeline>)
   ```

## Rules

- Always mark pricing as "Estimated" or "TBD" if not finalized — never guess
- Include explicit "Out of Scope" section to prevent scope creep
- Keep proposal to 1-2 pages (with optional appendices for detailed T&Cs)
- Match writing style to client email tone (formal vs. casual)
- If client has rejected proposals before, research why and address concerns
- Never include proprietary competitor names unless necessary for differentiation
- Use client's own language and terminology from their emails
- Pricing: if multi-phase, show per-phase breakdown and total
- Cross-reference to client file using [[wiki-links]]
- Product details in proposals must match PRODUCTS.md — never invent features or pricing.

## Templates

Use this structure for proposal file:

```markdown
# Proposal: [Project Name] for [Client Name]

**Date**: [YYYY-MM-DD]
**Prepared for**: [Contact Name, Title] | [Client Name]
**Valid until**: [date 30 days out]

---

## Executive Summary

[1-2 sentences on what you're proposing. 1-2 sentences on why this solves their stated problem.]

## Understanding [Client Name]

[Brief statement showing you understand their business, industry, or specific challenge they mentioned in discovery calls.]

## Proposed Scope

We will deliver the following for your [project area]:

- [deliverable 1 — brief description]
- [deliverable 2 — brief description]
- [deliverable 3 — brief description]
- [deliverable 4 — brief description]

## Deliverables & Timeline

| Phase | Deliverable | Due Date | Milestone |
|-------|-------------|----------|-----------|
| [Phase 1 name] | [output] | [date] | [outcome] |
| [Phase 2 name] | [output] | [date] | [outcome] |
| [Phase 3 name] | [output] | [date] | [outcome] |

**Total Duration**: [X weeks/months] from kickoff to final delivery.

## Investment

| Item | Rate/Fee | Quantity | Total |
|------|----------|----------|-------|
| [service/resource] | [cost] | [qty] | [subtotal] |

**Total Proposal Value**: $[total] | **Estimated investment**: $[value]

**Payment Terms**: [50% upfront, 50% at delivery] or [as billed monthly] or [other]

## What's Included

- [service 1]
- [service 2]
- [service 3]
- [ongoing support through delivery date]

## What's Not Included

- [out of scope item 1]
- [out of scope item 2]
- [out of scope item 3]

*Additional work beyond this scope will be quoted separately.*

## Next Steps

1. **Review** — Please review this proposal and let us know any questions
2. **Confirm** — Once confirmed, we'll send our standard service agreement
3. **Kickoff** — Upon signature, we'll schedule a kickoff meeting for [date range]
4. **Start** — Project begins [estimated start date]

---

**Questions?** Reply to this email or schedule time with [your name] at [your email].

*Attached: Standard Terms & Conditions*

---
[[clients/<client-slug>]] | [[sales/deals/<client-slug>]] | Last updated: [auto-date]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
