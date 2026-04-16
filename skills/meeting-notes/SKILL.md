---
name: meeting-notes
description: Capture, structure, and store meeting notes — extract decisions and action items, optionally push to Asana
argument-hint: "[paste notes or describe meeting]"
triggers:
  - "meeting notes"
  - "meeting summary"
  - "what happened in the meeting"
  - "log this meeting"
  - "capture meeting"
---

# Meeting Notes

Capture, structure, and store meeting notes. Extracts decisions and action items with owners and due dates. Optionally pushes action items to Asana.

## When to Trigger

- User mentions "meeting notes", "meeting summary", or "log this meeting"
- User pastes raw meeting content and asks to organize it
- After a calendar event that looks like a meeting

## Workflow

### Step 1: Gather Details

If the user pastes raw notes/transcript, extract details from it. Otherwise ask for:

1. **Date & time** of the meeting
2. **Attendees** — names and roles
3. **Topic/agenda** — what was discussed
4. **Key points** — decisions, outcomes, action items

If Calendar is connected, try to match to a calendar event for auto-filling date/time/attendees:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal events --today
```

### Step 2: Pull Vault Context

For each attendee, check if they exist in the vault:
- `~/.second-brain/vault/team/{name}.md` for team members
- `~/.second-brain/vault/clients/{name}.md` for clients

Use this context to enrich notes (roles, prior decisions, ongoing projects).

### Step 3: Structure Notes

Save to `~/.second-brain/vault/meetings/YYYY-MM-DD-<topic-slug>.md` using this template:

```markdown
# {Meeting Title}

**Date:** YYYY-MM-DD HH:MM
**Attendees:** {list with [[wiki-links]] to team/client files}
**Type:** {standup | sprint | client call | 1:1 | brainstorm | other}
**Related:** [[projects/{project}]] (if applicable)

## Agenda
- {agenda item 1}
- {agenda item 2}

## Discussion

### {Topic 1}
{Key points discussed}

### {Topic 2}
{Key points discussed}

## Decisions

| Decision | Context | Owner |
|----------|---------|-------|
| {what was decided} | {why} | {who owns it} |

## Action Items

- [ ] {action item} — **{owner}** — due {YYYY-MM-DD}
- [ ] {action item} — **{owner}** — due {YYYY-MM-DD}

## Notes
{Any additional context, raw content, or follow-up thoughts}
```

### Step 4: Save & Log

1. Write the file to `~/.second-brain/vault/meetings/`
2. Append to today's daily log:
   ```
   - **HH:MM** — Meeting notes saved: [[meetings/YYYY-MM-DD-topic-slug]]
   ```
3. Display a summary to the user with the decisions and action items highlighted

### Step 5: Push Action Items to Asana (if connected)

If Asana is enabled, ask the user:
> "I found {N} action items. Want me to create these as Asana tasks?"

If yes, for each action item:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task --name "{action}" --due "{date}" --notes "From meeting: {meeting title}"
```

If Asana is not connected or user declines, just keep them in the meeting notes.

### Step 6: Link to Previous Meetings

Search `~/.second-brain/vault/meetings/` for prior meetings with the same attendees or topic. If found, add a "Previous" link at the top:

```markdown
**Previous:** [[meetings/YYYY-MM-DD-prior-topic]]
```

## Naming Convention

`YYYY-MM-DD-<topic-slug>.md`

Examples:
- `2026-04-14-sprint-planning.md`
- `2026-04-14-client-sync-airtel.md`
- `2026-04-14-1on1-with-priya.md`

## Rules

- Decisions must be explicit and unambiguous — who decided what, and why
- Action items MUST have an **owner** and a **due date** when mentioned
- Use `[[wiki-links]]` to connect attendees and projects in the Obsidian graph
- Keep the raw content if the user pastes it — append under "## Notes", don't discard
- If the same meeting already has a file, append to it rather than creating a duplicate
- Don't ask too many questions — extract what you can from the content, ask only for what's missing

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
