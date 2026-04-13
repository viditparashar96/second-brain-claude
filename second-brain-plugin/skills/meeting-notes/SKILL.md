---
name: meeting-notes
description: Capture and organize meeting notes with a consistent template
triggers:
  - "meeting notes"
  - "meeting summary"
  - "what happened in the meeting"
  - "log this meeting"
---

# Meeting Notes

Use this skill to capture, organize, and store meeting notes in a consistent, searchable format.

## When to Trigger

- User mentions "meeting notes", "meeting summary", or "log this meeting"
- User pastes raw meeting content and asks to organize it
- After calendar events that look like meetings

## Workflow

1. **Gather details** — Ask for or extract: date, attendees, topic/agenda, and key content
2. **Load template** — Read `references/note-template.md` for the standard format
3. **Fill template** — Populate with meeting details, decisions, and action items
4. **Save to vault** — Write to `Dynamous/Memory/meetings/YYYY-MM-DD-<topic-slug>.md`
5. **Log reference** — Append a one-liner to today's daily log: `- **HH:MM** — Meeting notes saved to meetings/<filename>`
6. **Extract action items** — If there are clear action items with owners, mention them explicitly in the response

## Naming Convention

`YYYY-MM-DD-<topic-slug>.md`

Examples:
- `2026-04-13-sprint-planning.md`
- `2026-04-13-client-onboarding-acme.md`
- `2026-04-13-1on1-with-priya.md`

## Rules

- Use the template structure from `references/note-template.md` — don't freestyle
- Decisions should be explicit and unambiguous (who decided what, and why)
- Action items must have an **owner** and a **due date** if mentioned
- If attendees are in `team/`, pull their context (role, timezone) for richer notes
- Keep the raw content if the user pastes it — don't discard source material
