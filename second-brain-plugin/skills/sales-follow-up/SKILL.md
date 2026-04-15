---
name: sales-follow-up
description: Generate follow-up emails after meetings or for stale deals needing re-engagement
argument-hint: "[meeting|stale] [client-name] [optional-context]"
triggers:
  - "follow up"
  - "send follow-up"
  - "follow-up email"
  - "re-engage"
  - "stale deal"
  - "no activity"
  - "touch base"
---

# Follow-Up

Generate personalized follow-up emails after client meetings or for deals gone quiet. Two modes: post-meeting follow-ups with action items, or re-engagement emails for stale deals. Creates Gmail drafts for review — never auto-sends.

## When to Trigger

- After a client call or meeting, user needs to send a thank-you follow-up with next steps
- Deal has stalled (no contact for 7+ days) and needs re-engagement
- User says "follow up with [client]" or "re-engage [client]"
- Heartbeat detects deals with no recent activity requiring attention

## Workflow

### Mode A: Post-Meeting Follow-Up

1. **Extract meeting context** — Get client name and recent meeting details from user input

2. **Load recent meeting notes** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<client-name> meeting" --top-k 1
   ```
   Or read from recent vault entries: `~/.second-brain/vault/meetings/<date>-<client>.md`

3. **Extract from meeting notes**:
   - Commitments made (by you and client)
   - Next steps discussed
   - Action items and owners
   - Timeline for next interaction
   - Any concerns or objections raised

4. **Load client email tone** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<client-email>" --max 5
   ```
   Match tone, formality, terminology from past emails

5. **Generate follow-up email** with structure:
   - **Greeting** — Personalized, referencing meeting date/topic
   - **Thank you** — Brief thanks for their time, specific to discussion topic
   - **Recap** — 2-3 bullet points of commitments/next steps (client actions and yours)
   - **Action items** — Clear list: what you're doing and by when, what they need to do
   - **Timeline** — When you'll check in next, when client needs to decide/respond
   - **Closing** — Warm sign-off, offer to answer questions

6. **Create Gmail draft** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail draft --to "<client-email>" --subject "Follow-Up: [Meeting Topic] — [Your Name]" --body "<email-body>"
   ```
   Draft is never sent — user reviews before clicking send

7. **Save follow-up** to vault:
   ```bash
   ~/.second-brain/vault/sales/follow-ups/YYYY-MM-DD-<client-slug>-follow-up.md
   ```

8. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] Follow-up drafted: <client-name> — <key-action-items>
   ```

### Mode B: Stale Deal Re-Engagement

1. **Identify stale deals** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana search "" --status "In Progress" --max 20
   ```
   Find deals/tasks with no updates in 7+ days

2. **For each stale deal**, check **last contact date** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<client-email>" --max 1
   ```
   Get date of last email

3. **Load deal context** — Read vault file:
   ```bash
   cat ~/.second-brain/vault/clients/<client-slug>.md
   ```
   Extract: deal value, stage, what was being discussed

4. **Analyze why staled** — Check:
   - Is there a missing deliverable from you?
   - Is the client waiting for something?
   - Did you miss a promised follow-up?
   - Has timeline changed?

5. **Generate re-engagement email**:
   - **Subject** — Brief, not pushy (e.g., "Quick check-in on [project]")
   - **Opener** — Acknowledge the gap ("We haven't touched base in a couple weeks...")
   - **Reconnect** — What you remember from last conversation, show genuine interest
   - **Action** — Offer a specific next step: "Want to hop on a call to see where we stand?" or "I can send you an updated timeline by Friday"
   - **Urgency** — Hint at timeline without pressure ("I want to make sure we're still on track for [goal]")
   - **Closing** — Easy way to engage (link to calendar, email reply, etc.)

6. **Create Gmail draft** — Never sends, user reviews first

7. **Save re-engagement email** to:
   ```bash
   ~/.second-brain/vault/sales/follow-ups/YYYY-MM-DD-<client-slug>-reengagement.md
   ```

8. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] Re-engagement drafted: <client-name> — last contact [date]
   ```

## Rules

- **Post-meeting**: Always mention specific topics discussed to show you were paying attention
- **Post-meeting**: Include explicit deadlines (yours and theirs) for all action items
- **Post-meeting**: Send within 24 hours while conversation is fresh
- **Stale deals**: Don't be pushy or make them feel guilty; be genuinely curious about where they stand
- **Stale deals**: Include a clear, specific call to action (don't leave hanging)
- **Both modes**: Match email tone and formality to client's past emails
- **Both modes**: Use client's names and terminology from past conversations
- **Both modes**: Draft only — never auto-send emails
- Reference vault files using [[wiki-links]] to client and deal context

## Templates

### Post-Meeting Template

```markdown
Subject: Follow-Up: [Topic] — [Your Name]

Hi [Client First Name],

Thanks so much for taking time to speak with us today about [specific topic]. I really appreciated your insights on [specific thing they said].

Here's what we discussed:

- **Your action**: [what client committed to] by [date]
- **Our action**: [what you committed to] by [date]
- **Next step**: [when you'll reconnect — e.g., Thursday call, email decision, etc.]

I'll get [deliverable] to you by [date], and then we can [next milestone].

In the meantime, if any questions come up, don't hesitate to ping me.

Looking forward to the next step!

Best,
[Your Name]

---
[[clients/<client-slug>]] | [[sales/deals/<client-slug>]]
```

### Stale Deal Re-Engagement Template

```markdown
Subject: Quick Check-In: [Project Name]

Hi [Client First Name],

We haven't touched base in a few weeks and I wanted to make sure everything's on track with [project].

Last we spoke, we were working through [what was being discussed]. Any movement there, or has anything changed on your end?

I'd love to hop on a quick call this week to see where we stand and make sure we're aligned on next steps. Are you free for 15 minutes Tuesday or Wednesday?

Happy to work around your schedule.

Thanks,
[Your Name]

---
[[clients/<client-slug>]] | [[sales/deals/<client-slug>]]
```
