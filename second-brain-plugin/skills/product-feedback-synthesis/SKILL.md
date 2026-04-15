---
name: product-feedback-synthesis
description: Aggregate and analyze user and customer feedback to identify themes and priorities
argument-hint: "[topic-or-product-area] [optional: time-range]"
triggers:
  - "feedback synthesis"
  - "analyze feedback"
  - "user feedback"
  - "customer feedback"
  - "feedback themes"
  - "feedback analysis"
  - "what are users asking for"
  - "feature requests"
---

# Feedback Synthesis

Aggregate user and customer feedback across meetings, emails, research notes, and client files to identify patterns, common requests, pain points, and opportunities. Generates a prioritized synthesis report with supporting evidence and recommendations.

## When to Trigger

- Analyzing user feedback for a product area or feature
- Understanding customer pain points and feature requests
- Preparing for roadmap planning with prioritized feedback
- Decision-making on feature prioritization — what do users need most?
- Research phase before designing a new feature or product area
- Periodic feedback review (monthly, quarterly) to track evolving needs

## Workflow

1. **Extract topic/product area and optional time range** — Parse from user input
   - Topic examples: "authentication", "reporting", "mobile experience", "API", "pricing"
   - Time range: optional filter (last-month, last-quarter, all-time)

2. **Search vault for feedback sources** — Run queries across multiple sections:

   **Meeting Notes**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<topic> feedback request user" --path "meetings" --top-k 10
   ```
   Extract: client calls, user interviews, sales conversations capturing needs

   **Research Files**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<topic> research user feedback" --path "research" --top-k 10
   ```
   Extract: user research findings, interview notes, survey results, usability feedback

   **Client Files**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<topic> feedback pain point" --path "clients" --top-k 5
   ```
   Extract: feedback section from client vault files, customer requests, concerns

   **Email Search** (if Gmail connected):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "subject:<topic> OR body:<topic> feedback OR feature request OR problem" --max 20
   ```
   Extract: customer emails, support tickets, feature requests, complaints

3. **Analyze feedback for patterns** — Identify:
   - **Common Requests** — Features/capabilities mentioned multiple times, with frequency
   - **Pain Points** — Problems users are facing, blockers, frustrations
   - **Praise** — What users love, what's working well, core strengths
   - **Feature Gaps** — Capabilities missing vs. competitive offerings
   - **Usability Issues** — Friction points, confusing areas, workflows that don't work

4. **Generate synthesis report** with sections:

   - **Overview** — Topic analyzed, number of feedback sources, time period, high-level themes
   - **Top Themes** — 3-5 major patterns identified, with supporting quotes and frequency
   - **Common Feature Requests** — Prioritized list of requested capabilities
   - **Pain Points** — User frustrations, problems preventing adoption/usage
   - **Praise & Strengths** — What users love, competitive advantages
   - **Feature Gap Analysis** — Capabilities missing vs. alternatives
   - **Recommended Priorities** — Top 3-5 opportunities based on frequency and impact
   - **Evidence & Sources** — Quoted feedback with citations to vault sources using [[wiki-links]]

5. **Save synthesis report** to:
   ```bash
   ~/.second-brain/vault/product/feedback/YYYY-MM-DD-<topic-slug>-synthesis.md
   ```

6. **Link to related documents**:
   - Related PRDs that address feedback
   - Related projects or roadmap items
   - Research files or customer files used as sources

7. **Offer actionable next steps**:
   - Suggest creating PRDs for top-priority feedback items
   - Link to roadmap planning or OKR setting
   - Recommend customer communication on addressed feedback

8. **Log to daily log**:
   ```bash
   - **HH:MM** — [FEEDBACK] Synthesis: <topic> — <theme-count> themes, <request-count> feature requests, <sources> sources
   ```

## Rules

- Quote actual user feedback — paraphrasing loses credibility
- Frequency matters — feature requested by 1 user is different from requested by 10
- Distinguish between "nice to have" requests and "blocker" pain points
- Always cite sources with [[wiki-links]] so team can trace back to original feedback
- Synthesis should be balanced — include praise alongside pain points
- Time context matters — feedback from 6 months ago may be stale, recent feedback more relevant
- Recommended priorities should be data-driven, not gut feel
- Link feedback synthesis to PRDs, OKRs, and roadmap planning
- Consider source reliability — 1-on-1 customer feedback vs. unqualified internet comment has different weight

## Templates

Use this structure for the feedback synthesis file:

```markdown
# Feedback Synthesis: [Topic/Product Area]

**Date**: YYYY-MM-DD  
**Period Analyzed**: [e.g., Last Quarter]  
**Sources**: [count] feedback mentions across [count] sources  
**Synthesized By**: [name]

## Overview

[2-3 sentences: what topic, how many sources, what we learned, overall user sentiment]

## Top Themes

### Theme 1: [Theme Name]

**Frequency**: [number] mentions  
**Impact**: [high/medium/low — how important is this issue]

*Supporting Evidence*:
- "[Quote from user]" — [[source-link]]
- "[Quote from user]" — [[source-link]]
- "[Quote from user]" — [[source-link]]

**Analysis**: [Why this matters, user impact, business impact]

### Theme 2: [Theme Name]

[Same structure as Theme 1]

### Theme 3: [Theme Name]

[Same structure as Theme 1]

## Common Feature Requests

1. **[Feature Request]** — Requested by [count] users
   - Use case: [how they'd use it]
   - Mentioned in: [[source-link]]

2. **[Feature Request]** — Requested by [count] users
   - Use case: [how they'd use it]
   - Mentioned in: [[source-link]]

3. **[Feature Request]** — Requested by [count] users
   - Use case: [how they'd use it]
   - Mentioned in: [[source-link]]

## Pain Points & Frustrations

- **[Pain Point]**: [description], Mentioned by [count] users
  - Impact: [what's at stake — adoption, retention, revenue]
  - Sources: [[links]]

- **[Pain Point]**: [description], Mentioned by [count] users
  - Impact: [what's at stake]
  - Sources: [[links]]

## What Users Love

- **[Strength]**: [description], Praised by [count] users
  - Quotes: "[positive feedback]"
  - Competitive advantage: [why this matters]

- **[Strength]**: [description], Praised by [count] users
  - Quotes: "[positive feedback]"

## Feature Gap Analysis

| Capability | Our Product | Competitor A | Competitor B | Priority |
|------------|-------------|--------------|--------------|----------|
| [feature] | No | Yes | No | High |
| [feature] | Basic | Advanced | Advanced | Medium |
| [feature] | Yes | Yes | No | Medium |

## Recommended Priorities

### Priority 1: [Feature/Pain Point]

**Rationale**: 
- Mentioned by [count] users
- Impact: [business value if addressed]
- Effort estimate: [T-shirt size]
- Recommendation: [[PRD for feature]] or [[OKR item]]

### Priority 2: [Feature/Pain Point]

**Rationale**: [same structure]

### Priority 3: [Feature/Pain Point]

**Rationale**: [same structure]

## Next Steps

- [ ] Create PRD for Priority 1: [feature]
- [ ] Communicate to customers: addressing [pain point]
- [ ] Schedule roadmap discussion with stakeholders
- [ ] Reach out to [count] users who mentioned [pain point] — share timeline

---
[[product/prds]] | [[product/okrs]] | [[projects]]
```
