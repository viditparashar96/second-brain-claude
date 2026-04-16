---
name: product-prd-drafter
description: Generate Product Requirements Documents from notes, discussions, or rough ideas
argument-hint: "[feature-name] [description-or-notes]"
triggers:
  - "create PRD"
  - "draft PRD"
  - "PRD for"
  - "write requirements"
  - "product requirements"
  - "feature spec"
  - "spec out feature"
---

# PRD Drafter

Generate structured Product Requirements Documents from rough notes, meeting transcripts, or feature ideas. Pulls project context, past decisions, and user feedback from memory to create comprehensive, actionable PRDs.

## When to Trigger

- User has rough notes about a feature and needs a formal PRD
- Feature discussed in a meeting — capture decision and formalize requirements
- User asks "create PRD for [feature]" or provides raw feature description
- Need to align team on feature scope, goals, and success metrics
- Converting a Slack discussion or email thread into formal documentation

## Workflow

1. **Extract feature name and description** — Parse from user input or paste notes/transcript

2. **Check product registry** — From PRODUCTS.md (already in session context), verify whether this is a new product or an enhancement to an existing one. If existing, pull current features, tech stack, known issues, and roadmap to ensure the PRD builds on what exists.

3. **Search for related project context** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<feature-name> project context requirements" --top-k 5
   ```
   Find: existing project docs, past feature discussions, related decisions

4. **Load project vault file** — If available:
   ```bash
   cat ~/.second-brain/vault/projects/<project-slug>.md
   ```
   Extract: project goals, audience, current phase, constraints, roadmap

5. **Search for user feedback** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<feature-name> feedback user requests" --top-k 5
   ```
   Find: customer asks, pain points, research notes related to this feature

6. **Check Asana for related tasks** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana search "<feature-name>" --max 10
   ```
   Extract: existing work, dependencies, assigned owners, timeline context

7. **Generate structured PRD** with sections:
   - **Problem Statement** — What problem does this solve? For whom?
   - **Goals & Success Metrics** — What success looks like (measurable)
   - **User Stories** — 3-5 stories in "As a [role], I want [action], so that [benefit]" format
   - **Functional Requirements** — What the feature does, step-by-step
   - **Non-Functional Requirements** — Performance, security, scalability, data, compliance
   - **Design Considerations** — UI/UX, accessibility, integrations
   - **Out of Scope** — What we're explicitly NOT doing (prevents scope creep)
   - **Open Questions** — Assumptions to validate, decisions pending
   - **Dependencies** — Other work that must happen first
   - **Timeline Estimate** — T-shirt size and reasoning
   - **Related Links** — Cross-references to project, feedback sources, related PRDs

8. **Save PRD** to:
   ```bash
   ~/.second-brain/vault/product/prds/YYYY-MM-DD-<feature-slug>.md
   ```

9. **Offer Asana integration** — Ask if user wants to create epic/milestone tasks in Asana

10. **Log to daily log**:
   ```bash
   - **HH:MM** — [PRODUCT] PRD created: <feature-name> — <goal-summary>
   ```

## Rules

- PRD should be 2-3 pages, detailed but concise
- Always include success metrics — vague goals become vague features
- User stories ground requirements in real use cases
- Flag assumptions clearly in "Open Questions" section
- Link to supporting evidence (feedback, meeting notes) using [[wiki-links]]
- If project context missing, note it as a knowledge gap to fill
- Keep Out of Scope section crisp — prevents scope creep later
- Cross-reference related PRDs if this feature depends on or relates to others
- PRDs for existing products must reference PRODUCTS.md to avoid contradicting current features or architecture.

## Templates

Use this structure for the PRD file:

```markdown
# PRD: [Feature Name]

**Date**: YYYY-MM-DD  
**Owner**: [name if known]  
**Project**: [[projects/<project-slug>]]  
**Status**: Draft

## Problem Statement

[What problem does this solve? For whom? Why is it urgent/important?]

## Goals & Success Metrics

- **Goal 1**: [outcome we're targeting]
  - Metric: [measurable indicator] — Target: [value]
- **Goal 2**: [outcome we're targeting]
  - Metric: [measurable indicator] — Target: [value]

## User Stories

- As a [role], I want [action], so that [benefit]
- As a [role], I want [action], so that [benefit]
- As a [role], I want [action], so that [benefit]

## Functional Requirements

1. [Feature capability]
2. [Feature capability]
3. [Feature capability]

## Non-Functional Requirements

- **Performance**: [target latency, throughput]
- **Security**: [authentication, data handling, compliance]
- **Scalability**: [expected growth, load handling]
- **Data**: [storage, retention, privacy considerations]

## Design Considerations

[UI/UX principles, accessibility, integration points, API design]

## Out of Scope

- [Explicitly NOT doing this]
- [Explicitly NOT doing this]

## Open Questions

- [ ] [Assumption or decision to validate]
- [ ] [Assumption or decision to validate]

## Dependencies

- [Other work that must complete first]
- [Third-party integrations needed]

## Timeline Estimate

- **T-shirt Size**: [S/M/L/XL]
- **Rationale**: [why this size]

---
[[projects/<project-slug>]] | [[product/feedback/<topic>-synthesis]]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
