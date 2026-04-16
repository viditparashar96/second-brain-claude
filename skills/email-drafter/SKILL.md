---
name: email-drafter
description: Draft client emails and reply drafts in Vidit's voice using Gmail integration
triggers:
  - "draft an email"
  - "draft a reply"
  - "email to client"
  - "write an email"
  - "reply to this email"
---

# Email Drafter

Use this skill to draft client emails and reply drafts in Vidit's voice. Creates Gmail drafts — never sends. Uses RAG on past sent drafts for voice-matching.

## When to Trigger

- User asks to draft an email or reply
- Heartbeat detects unreplied emails from clients/team needing a response
- User says "draft an email", "reply to this email", or "email to client"

## Workflow

### For new client emails (about org products):
1. **Get context** — Ask: who is the recipient, what product/topic, what's the goal?
2. **Pull client context** — Check `Dynamous/Memory/clients/<client-name>.md` for history, preferences, past interactions
3. **Match voice** — Run: `.venv/bin/python .claude/scripts/memory_search.py "client email" --path-prefix drafts/sent --top-k 3 --json` to find similar past emails
4. **Load tone guide** — Read `references/tone-guide.md` for writing style rules
5. **Draft the email** — Write the draft following the tone guide
6. **Create Gmail draft** — Run: `.venv/bin/python .claude/scripts/integrations/query.py gmail draft --to "<addr>" --subject "<subject>" --body "<body>"`
7. **Save to vault** — Write draft to `Dynamous/Memory/drafts/active/YYYY-MM-DD_email_<slug>.md` with YAML frontmatter
8. **Log** — Append to daily log: `- **HH:MM** — Drafted email to <recipient> re: <subject>`

### For reply drafts:
1. **Read the original** — Run: `.venv/bin/python .claude/scripts/integrations/query.py gmail read <message_id>`
2. **Pull context** — Search vault for relevant context about the sender/topic
3. **Match voice** — Search `drafts/sent/` for similar past replies
4. **Draft the reply** — Write a contextual reply following the tone guide
5. **Create Gmail draft** — Same as above, with `--reply-to <original_message_id>` for threading
6. **Save to vault** — Write to `drafts/active/` with frontmatter including `source_id`
7. **Log** — Append to daily log

## Draft File Format (for vault)

```yaml
---
type: email
source_id: <gmail_message_id or empty for new emails>
recipient: recipient@example.com
subject: "Subject line"
context: "Brief context about why this draft was created"
created: 2026-04-13T14:30:00+05:30
status: active
---

## Original Message
<if reply: paste the original email content>

## Draft Reply
<the drafted email text>
```

## Rules

- **Never send.** Only create Gmail drafts and vault files. Vidit reviews and sends manually.
- **Match Vidit's voice.** Professional but not stiff. Concise. Technically precise. No corporate fluff.
- **Always include context.** If replying, reference what the original email was about.
- **Keep it short.** Most emails should be 3-5 sentences. Only go longer if the topic requires it.
- **Client product emails** should pull specifics from `clients/` — don't be generic.
- **If unsure about tone**, err on the side of direct and helpful.

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
