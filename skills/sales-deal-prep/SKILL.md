---
name: sales-deal-prep
description: Generate pre-meeting brief for client/prospect calls with context and talking points
argument-hint: "[client-name] [meeting-context]"
triggers:
  - "prep for meeting"
  - "client brief"
  - "deal prep"
  - "upcoming call"
  - "meeting preparation"
  - "prepare for call"
---

# Deal Prep

Generate a comprehensive pre-meeting brief for client and prospect calls. Pulls email history, relationship context, open tasks, and past interactions to build structured talking points.

## When to Trigger

- User has an upcoming client or prospect call and needs background
- Meeting scheduled in calendar — pull context before the call
- User asks "prep for [client]" or "what do I need to know about [client]"
- Heartbeat detects upcoming meetings requiring preparation

## Workflow

1. **Extract client/prospect name** — Parse from user input (e.g., "prep for Acme Corp")

2. **Search email history** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<client-email> OR to:<client-email>" --max 20
   ```
   Extract recent emails, tone, key topics, and any open questions

3. **Load client context** — Read vault file:
   ```bash
   cat ~/.second-brain/vault/clients/<client-slug>.md
   ```
   Extract: company overview, relationship history, contact info, deal status, pain points

4. **Pull product context** — Check PRODUCTS.md (already in session context) to identify which products are relevant to this client/deal. Pull features, pricing, competitive edge, and key clients for the relevant product(s).

5. **Search meeting notes** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<client-name> meeting notes" --top-k 5
   ```
   Find past interactions, decisions, and commitments

6. **Check Asana for open tasks** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana search "<client-name>" --status "Not Started,In Progress"
   ```
   List deliverables, proposals, or action items related to this deal

7. **Generate structured brief** with sections:
   - **Client Overview** — Company, industry, size, key contact info
   - **Relationship History** — How long engaged, past wins/losses, key decisions
   - **Last Interaction** — Date, topic, outcomes, open commitments
   - **Current Deal Status** — Stage, value (if available), timeline, blockers
   - **Open Action Items** — Proposals due, decisions pending, follow-ups needed
   - **Talking Points** — 3-5 key topics to cover, based on email and meeting history
   - **Call Goals** — What needs to happen in this meeting (close, advance, unblock, etc.)

8. **Save brief** to:
   ```bash
   ~/.second-brain/vault/sales/briefs/YYYY-MM-DD-<client-slug>.md
   ```

9. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] Deal prep: <client-name> call — <brief-summary>
   ```

## Rules

- If client vault file doesn't exist, still generate brief from emails and Asana
- Use email tone to match communication style for this client
- Highlight any red flags or stalled deals (last contact >2 weeks ago)
- Include specific names and dates from past interactions
- If upcoming call time is known, note it at top of brief
- Keep brief to 1-2 pages (concise, actionable)
- Cross-reference vault links using [[wiki-links]] to client file and past briefs
- Always reference PRODUCTS.md for product-specific details — never invent pricing, features, or competitive claims.

## Templates

Use this structure for the brief file:

```markdown
# Deal Prep: [Client Name] — [Date & Time]

## Client Overview
- **Company**: [name]
- **Industry**: [sector]
- **Contact**: [name, title, email]
- **Relationship Stage**: [prospect, lead, customer, renewal]

## Relationship History
[3-4 sentences on how long engaged, key wins, relationship strength]

## Last Interaction
- **Date**: [YYYY-MM-DD]
- **Topic**: [what was discussed]
- **Outcome**: [what was decided/committed]

## Current Deal Status
- **Stage**: [qualify, propose, negotiate, close]
- **Value**: [$amount if known]
- **Timeline**: [expected close date]
- **Blockers**: [what's preventing progress]

## Open Action Items
- [ ] [deliverable] — due [date]
- [ ] [deliverable] — due [date]

## Talking Points
1. [topic based on email history]
2. [topic based on past decisions]
3. [topic addressing current blocker]
4. [topic from their stated pain point]
5. [topic about competitive positioning or unique value]

## Call Goals
- **Primary**: [what must happen — close, advance, unblock, etc.]
- **Secondary**: [what would be good to cover]
- **Success Metric**: [how will we know this meeting was successful]

---
[[clients/<client-slug>]] | [[sales/proposals/<client-slug>]]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
