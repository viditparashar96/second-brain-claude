---
name: meeting-prep
description: Generate a pre-meeting brief by pulling calendar event details, attendee context from vault, and previous meeting history
argument-hint: "[meeting name or time]"
triggers:
  - "prep for meeting"
  - "meeting prep"
  - "meeting brief"
  - "prepare for meeting"
  - "what do I need for my next meeting"
  - "brief me on"
---

# Meeting Prep Brief

Generate a focused pre-meeting brief by combining calendar data, vault context, and meeting history.

## Workflow

### Step 1: Identify the Meeting

If the user specifies a meeting name or time, use that. Otherwise:

1. Check today's calendar:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal events --today
   ```
2. If multiple events, ask the user which one. If one upcoming event, use that.
3. If no calendar integration, ask the user for: meeting topic, attendees, and time.

### Step 2: Gather Context

Run these searches in parallel:

**a) Attendee context** — For each attendee name or email:
- Search `~/.second-brain/vault/team/` for team member files
- Search `~/.second-brain/vault/clients/` for client files
- Extract: role, recent interactions, preferences, notes

**b) Previous meetings** — Search for prior meeting notes with same attendees or topic:
- Search `~/.second-brain/vault/meetings/` for matching files
- Extract: last meeting date, key decisions, open action items

**c) Project context** — If the meeting relates to a known project:
- Search `~/.second-brain/vault/projects/` for the project file
- Extract: current status, blockers, recent updates

**d) Open action items** — Check if there are overdue items assigned to attendees:
- Scan recent meeting notes for unchecked `- [ ]` items involving attendees
- If Asana is connected:
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana tasks
  ```

### Step 3: Generate Brief

Assemble a prep brief in this format:

```markdown
# Meeting Brief: {title}

**When:** {date} {time}
**Attendees:** {list with roles/context}
**Location/Link:** {location or Meet link}

## Context
{1-3 sentences on what this meeting is about, based on event description + vault context}

## Attendee Notes
{For each attendee: name, role, key context from vault}

## From Last Meeting
{Date of last meeting with same group, key decisions, open action items}

## Open Items
{Action items from previous meetings that are still unresolved}
{Overdue Asana tasks relevant to attendees}

## Suggested Talking Points
{3-5 suggested topics based on open items, project status, and meeting context}
```

### Step 4: Save & Log

1. Display the brief to the user
2. Log to today's daily log: `- **HH:MM** — Meeting prep generated for {title}`
3. Do NOT save the brief as a file unless the user asks — it's ephemeral context

## Rules

- Pull from vault first, then integrations — vault context is richer
- Use `[[wiki-links]]` when referencing vault files so user can navigate in Obsidian
- If no context is found for an attendee, say so — don't fabricate
- Keep the brief scannable — bullet points over paragraphs
- If Calendar isn't connected, still work with whatever the user provides manually

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
