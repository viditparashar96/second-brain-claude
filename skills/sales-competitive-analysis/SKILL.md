---
name: sales-competitive-analysis
description: Maintain and search competitive battle cards with objections, strengths, and win strategies
argument-hint: "[lookup|update|create] [competitor-name] [optional-data]"
triggers:
  - "competitor analysis"
  - "battle card"
  - "what do we know about"
  - "competitive positioning"
  - "our vs their"
  - "how do we compete"
---

# Competitive Analysis

Maintain and search a library of competitive battle cards. Lookup competitor info before calls, add new intelligence when you learn it, and surface battle cards to support positioning against specific competitors.

## When to Trigger

- Before a client call, user asks "what do we know about [competitor]"
- After a call/email, user learns new competitive intelligence to log
- User needs to create a new battle card for an emerging competitor
- Heartbeat detects competitor mention in emails/deals and prompts card lookup
- User asks "how do we compete against [competitor]"

## Workflow

### Lookup Mode: Search Competitor Info

1. **Extract competitor name** from user input

2. **Pull product context** — From PRODUCTS.md (already in session context), pull the relevant product's competitive edge, pricing, and key features to compare against the competitor.

3. **Load battle card** — Read vault file:
   ```bash
   cat ~/.second-brain/vault/sales/competitors/<competitor-slug>.md
   ```
   If file doesn't exist, search vault memory for any mentions

4. **Search vault for recent intelligence** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<competitor-name> pricing strengths weaknesses objections" --top-k 5
   ```

5. **Search email history** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "<competitor-name>" --max 10
   ```
   Extract any mentions of competitor pricing, positioning, or customer feedback

6. **Display battle card** — Show user the file with:
   - Company overview (what they do)
   - Key strengths (what they're good at)
   - Key weaknesses (where they struggle)
   - Pricing comparison (vs. our pricing)
   - Common objections (what clients say when comparing)
   - Win strategies (how we beat them)
   - Recent intelligence (latest info, last updated)

7. **Update last-accessed date** in battle card

8. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] Competitor lookup: <competitor-name>
   ```

### Update Mode: Add New Intelligence

1. **Extract competitor name and intelligence** from user input (what they learned)

2. **Pull product context** — From PRODUCTS.md (already in session context), verify current positioning and pricing to contextualize the new intelligence.

3. **Load existing battle card** — Read:
   ```bash
   cat ~/.second-brain/vault/sales/competitors/<competitor-slug>.md
   ```

4. **Parse the new intel**:
   - Is it about pricing?
   - Is it about a new feature/weakness?
   - Is it feedback from a lost deal (objection)?
   - Is it about market position or customer perception?

5. **Update battle card** with new intelligence:
   - Add to "Recent Intelligence" section with date
   - Update relevant section (strengths/weaknesses/objections if applicable)
   - Keep history of changes (don't delete old info)

6. **Save updated file**

7. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] Competitive intel: <competitor-name> — <intel-summary>
   ```

### Create Mode: New Competitor Card

1. **Extract competitor name** from user input

2. **Pull product context** — From PRODUCTS.md (already in session context), identify our product positioning and key differentiators to inform the initial competitive positioning.

3. **Search for public info** — Run:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<competitor-name> website pricing features" --top-k 3
   ```

4. **Generate battle card template** with initial info:
   - Company overview (from their website/LinkedIn, if available)
   - Key products/services
   - Estimated pricing (if public)
   - Strengths (based on market position)
   - Weaknesses (gaps vs. your offering)
   - Objections (what prospects typically say)
   - Win strategies (placeholder for initial thoughts)
   - Intelligence log (with creation date)

5. **Save new battle card** to:
   ```bash
   ~/.second-brain/vault/sales/competitors/<competitor-slug>.md
   ```

6. **Log to daily log**:
   ```bash
   - **HH:MM** — [SALES] New competitor card: <competitor-name>
   ```

## Rules

- **Battle cards are knowledge base, not opinions** — log facts, customer feedback, and observable market position
- **Keep history** — when updating, timestamp new info and don't delete old entries
- **Reference sources** — if you learned something from a customer, email, or call, note the source (without revealing confidential client names)
- **Update regularly** — mark "last-updated" date on all cards
- **Before calls** — lookup battle card for competitor if expected to be mentioned
- **After calls** — add any new intelligence learned (pricing, positioning, objections)
- **Never assume** — if you're not sure about pricing or features, mark as "estimated" or "needs verification"
- **Cross-reference** — link battle cards to deals/clients where that competitor was mentioned using [[wiki-links]]
- Competitive analysis must reference PRODUCTS.md for accurate product positioning — never invent claims.

## Templates

Use this structure for battle card files:

```markdown
# Battle Card: [Competitor Name]

**Last Updated**: [YYYY-MM-DD]
**Market Position**: [emerging/established/leader/niche]

---

## Company Overview

[1-2 sentences on what they do, who they target, how established they are]

### Key Leadership
- [Founder/CEO name]
- [Other notable executives]

---

## Products & Services

- **Primary offering**: [description]
- **Secondary offerings**: [list]
- **Target customer**: [company size, industry, use case]

---

## Pricing

| Tier | Cost | What's Included | How It Compares to Us |
|------|------|-----------------|----------------------|
| [Tier 1] | [price/range] | [features] | [vs. our tier] |
| [Tier 2] | [price/range] | [features] | [vs. our tier] |
| [Tier 3] | [price/range] | [features] | [vs. our tier] |

**Notes**: [Is pricing public? Enterprise discounts? Per-seat vs. flat? Any custom pricing we've heard about?]

---

## Key Strengths

- [Strength 1]: [why it matters to customers, specific example if known]
- [Strength 2]: [why it matters to customers, specific example if known]
- [Strength 3]: [why it matters to customers, specific example if known]

---

## Key Weaknesses & Gaps

- [Weakness 1]: [what they don't do well, impact on customer experience]
- [Weakness 2]: [what they don't do well, impact on customer experience]
- [Weakness 3]: [what they don't do well, impact on customer experience]

**Our advantage**: [How we position ourselves better in these gaps]

---

## Common Objections & Win Strategies

When prospect mentions [competitor], they typically say:

1. **Objection**: "[Common complaint/advantage they state]"
   - **Our response**: [How we address this]
   - **Example talking point**: [Specific example or story]

2. **Objection**: "[Common complaint/advantage they state]"
   - **Our response**: [How we address this]
   - **Example talking point**: [Specific example or story]

3. **Objection**: "[Common complaint/advantage they state]"
   - **Our response**: [How we address this]
   - **Example talking point**: [Specific example or story]

---

## Recent Intelligence

- **[YYYY-MM-DD]**: [New feature/pricing/market move we learned about] — [source if safe to note]
- **[YYYY-MM-DD]**: [Customer feedback or objection we encountered] — [source if safe to note]
- **[YYYY-MM-DD]**: [Pricing change or new positioning] — [source if safe to note]

---

## Sales Playbook

### If prospect has already chosen them:
[How to reposition and potentially win back]

### If prospect is comparing:
[Key differentiators to emphasize]

### If prospect is currently using them:
[Common reasons they switch away, migration path we offer]

---

## Related Deals & Opportunities

[Cross-reference vault links to deals where this competitor was mentioned]
- [[sales/deals/client-name]]
- [[sales/deals/client-name]]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
