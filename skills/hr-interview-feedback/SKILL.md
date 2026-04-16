---
name: hr-interview-feedback
description: Structure interview feedback into a consistent scorecard format with hiring recommendation
argument-hint: "[paste raw interview notes or describe candidate]"
triggers:
  - "interview feedback"
  - "interview notes"
  - "candidate feedback"
  - "structure interview notes"
  - "candidate scorecard"
---

# Interview Feedback

Convert raw interviewer notes into a structured scorecard with competency ratings, red/green flags, and hiring recommendation. Searches vault for role requirements to contextualize feedback.

## When to Trigger

- User pastes raw interview notes and asks to organize them
- User mentions "interview feedback", "candidate scorecard", or "interview notes"
- User wants to document feedback before a hiring discussion
- Feedback gathering round for a candidate

## Workflow

### Step 1: Gather Interview Details

Ask for (or extract from pasted notes):

1. **Candidate name** and role applied for
2. **Interview date** and interviewer(s)
3. **Raw notes** — unstructured feedback, observations, impressions
4. **Interview type** — phone screen, technical, behavioral, system design, culture fit, other

### Step 2: Find Role Context

Search vault for role requirements:
Use the `search_memory` MCP tool with query: "role {role_name} requirements"

If found, note key competencies expected (technical skills, communication level, domain knowledge, leadership needs).

### Step 3: Structure the Scorecard

Create a scorecard file at `~/.second-brain/vault/hr/interviews/YYYY-MM-DD-<candidate-slug>.md`:

```markdown
# Interview Feedback: {Candidate Name}

**Date:** YYYY-MM-DD
**Role:** {Role Title}
**Interviewer(s):** {Names}
**Interview Type:** {Type}

## Candidate Summary

{1-2 sentence overall impression}

## Competency Ratings

Rate on 1-5 scale (1=poor, 3=meets expectations, 5=exceptional):

| Competency | Rating | Evidence |
|------------|--------|----------|
| Technical Skills | {1-5} | {Specific example or observation} |
| Communication | {1-5} | {How they explained, asked questions, articulated ideas} |
| Problem Solving | {1-5} | {How they approached challenges, examples given} |
| Culture Fit | {1-5} | {Values alignment, team compatibility} |
| Domain Knowledge | {1-5} | {Depth of relevant experience} |

## Red Flags

- {Concern 1 with context}
- {Concern 2 with context}
- {Concern 3 if any}

(Leave empty if none)

## Green Flags

- {Strength 1 with example}
- {Strength 2 with example}
- {Strength 3 with example}

## Hiring Recommendation

**Overall Score:** {Average of ratings} / 5

**Recommendation:** {Strong Yes | Yes | Undecided | No | Strong No}

**Reasoning:** {Why this recommendation — weighing strengths vs concerns}

**Next Steps:** {Phone screen → technical → onsite | Schedule debrief | Decline | Request additional interview}

## Notes

{Raw feedback, verbatim quotes, additional context, comparisons to other candidates if relevant}
```

### Step 4: Extract Key Signals

Analyze the notes for:
- **Confidence level** — Do they understand the role and domain?
- **Learning ability** — Can they grow into gaps?
- **Team fit** — Would they collaborate well?
- **Red flags** — Any deal-breakers (culture mismatch, dishonesty, overqualified with flight risk)?

### Step 5: Save & Log

1. Write the scorecard file
2. Append to daily log:
   ```
   - **HH:MM** — Interview feedback captured: [[hr/interviews/YYYY-MM-DD-candidate-slug]] — {Overall Rec}
   ```
3. Display summary to user

### Step 6: Create Asana Task (Optional)

If Asana is connected, ask:
> "Want me to create a hiring discussion task for the team?"

If yes:
Use the `list_tasks` MCP tool (task creation via Asana API — log the action item with `log_note` instead)

## Naming Convention

`YYYY-MM-DD-<candidate-first-last>.md`

Examples:
- `2026-04-14-sarah-chen.md`
- `2026-04-10-marcus-thompson.md`

## Rules

- **Be specific** — Use quotes and examples, not vague impressions
- **Separate fact from interpretation** — "Asked about concurrency bugs (fact)" vs "seemed uncomfortable with multi-threading (interpretation)"
- **Rating scale consistency** — Use the same 1-5 scale across all interviews for comparability
- **Red flags must be explicit** — Don't bury concerns; call them out clearly with context
- **No anonymous feedback** — Always include interviewer name
- **Scores should reflect role requirements** — A 3 in leadership might be right for IC roles, unacceptable for managers
- Do not create scorecard until you have at least 70% of the information

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
