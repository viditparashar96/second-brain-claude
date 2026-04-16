---
name: ops-vendor-management
description: Track vendor relationships, contracts, SLAs, and automate renewal preparation
argument-hint: "[add|review|list|renew] [vendor-name] [optional-details]"
triggers:
  - "add vendor"
  - "vendor review"
  - "vendor evaluation"
  - "contract renewal"
  - "vendor renewal"
  - "vendor list"
  - "vendor performance"
  - "vendor renewal prep"
  - "vendor management"
---

# Vendor Management

Track and evaluate vendor relationships, contracts, and performance. Automates renewal preparation by pulling communication history and flagging upcoming contract milestones.

## When to Trigger

- User needs to add a new vendor/service provider to tracking
- Vendor contract is approaching renewal deadline
- User needs to evaluate vendor performance for renewal decision
- Vendor relationship needs review or performance assessment
- User says "manage vendor [name]" or "review vendor for [service]"
- Calendar shows upcoming contract renewal date

## Workflow

1. **Extract parameters** — Parse from user input:
   - Vendor name
   - Service/product provided
   - Command (add, review, list, renew)
   - For "add": contact info, contract dates, costs, SLA terms
   - For "review": evaluation period, focus areas (performance, cost, service)

2. **For ADD command** — Create vendor profile:
   - Search Gmail for vendor communications:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<vendor-domain> OR to:<vendor-domain>" --max 20
     ```
   - Extract: contact names, support channels, communication frequency
   - Search vault for related vendor info:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "<vendor-name> contract SLA" --top-k 3
     ```

3. **For REVIEW command** — Evaluate vendor performance:
   - Load vendor profile:
     ```bash
     cat ~/.second-brain/vault/ops/vendors/<vendor-slug>.md
     ```
   - Search for incident/complaint history:
     ```bash
     grep -r "<vendor-name>\|incident\|issue\|downtime\|complaint" ~/.second-brain/vault/daily/ | tail -30
     ```
   - Retrieve recent emails for sentiment analysis:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<vendor-email>" --max 15
     ```
   - Generate performance scorecard: uptime %, responsiveness, cost efficiency, feature delivery

4. **For RENEW command** — Prepare renewal negotiation:
   - Load current contract:
     ```bash
     cat ~/.second-brain/vault/ops/vendors/<vendor-slug>.md
     ```
   - Calculate days until renewal expiration
   - Search calendar for renewal deadline:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal search "<vendor-name> renewal\|contract deadline" --max 5
     ```
   - Pull 6-12 month email history with vendor:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gmail search "from:<vendor-email>" --max 50
     ```
   - Create negotiation brief with:
     - Current terms vs. market rates
     - Performance metrics and issues
     - Leverage points (competitor options)
     - Must-haves for renewal vs. nice-to-haves

5. **For LIST command** — Display all vendors:
   ```bash
   ls -la ~/.second-brain/vault/ops/vendors/*.md | sort
   ```
   Generate summary table: vendor name, service, contract end date, status (active/renewal-due/at-risk)

6. **Generate vendor profile document** with sections:
   - **Company Profile** — Name, headquarters, industry, founded year
   - **Service/Product** — What they provide, critical for operations (Y/N)
   - **Key Contacts** — Primary contact, support team, escalation contact
   - **Contract Terms**:
     - Contract start date, end date, renewal date
     - Auto-renewal terms (Y/N), notice period required
     - Annual cost, payment schedule (monthly, annually, etc.)
   - **SLA & Performance Metrics**:
     - Uptime SLA %, support response time, availability window
     - Historical performance score (0-100)
     - Recent incidents and resolutions
   - **Performance Notes** — Strengths, weaknesses, reliability, responsiveness
   - **Renewal Status** — Days until renewal, decision needed by [date]
   - **Alternatives Considered** — Competitor options with cost/feature comparison
   - **Last Review** — Date reviewed, reviewer, decision

7. **Save vendor profile** to:
   ```bash
   ~/.second-brain/vault/ops/vendors/<vendor-slug>.md
   ```
   Include YAML frontmatter:
   ```yaml
   ---
   vendor_name: "[Name]"
   service: "[Service]"
   contract_end: "[YYYY-MM-DD]"
   status: "active|renewal-due|at-risk|inactive"
   cost_annual: "$[amount]"
   last_reviewed: "[YYYY-MM-DD]"
   ---
   ```

8. **Add renewal date to calendar** if renewing:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal create-event \
     --title "Vendor Renewal Deadline: [vendor-name]" \
     --date "[renewal-date]" \
     --reminder "14 days before"
   ```

9. **Optionally create Asana task** for renewal action:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" asana create-task \
     --project "Operations" \
     --name "Renew contract: [vendor-name] (due YYYY-MM-DD)" \
     --due-date "[30-days-before-expiry]"
   ```

10. **Log to daily log**:
    ```bash
    - **HH:MM** — [OPS] Vendor [action]: <vendor-name> — Status: <status> — Renewal: <renewal-date>
    ```

## Rules

- Contract end dates are critical — flag if less than 30 days remaining
- Always search for recent vendor communications before renewal to assess satisfaction
- Performance score should be objective: calculate from uptime %, support response times, incident count
- Mark vendors as "at-risk" if performance score drops below 70 or they've had 2+ incidents in 6 months
- Never commit to renewal without reviewing performance metrics and comparing alternatives
- Renewal notices must be sent by date specified in contract (typically 30-90 days before expiry)
- Cost comparisons: always include not just subscription cost but implementation, training, switching costs
- Document any escalations or service issues in "Performance Notes"
- Use [[wiki-links]] to reference related projects, contracts, and team members

## Templates

Use this structure for vendor profile file:

```markdown
---
vendor_name: "[Vendor Legal Name]"
service: "[Service/Product Category]"
website: "[URL]"
contract_start: "[YYYY-MM-DD]"
contract_end: "[YYYY-MM-DD]"
auto_renewal: true|false
renewal_notice_required: "[days before expiry]"
status: "active|renewal-due|at-risk|inactive"
cost_annual: "$[amount]"
payment_schedule: "monthly|annual|[other]"
last_reviewed: "[YYYY-MM-DD]"
---

# [Vendor Name] — Vendor Profile

## Company Profile

**Legal Name**: [Full legal name]  
**Headquarters**: [City, Country]  
**Industry**: [Industry/Category]  
**Founded**: [Year]  
**Website**: [URL]  
**Customer Support**: [support email/phone/hours]

## Service / Product

**What They Provide**: [Description of service, 2-3 sentences]

**Critical for Operations**: [Yes/No] — Reason: [if yes, why is this critical]

**Usage**: [How we use it, primary users/teams]

## Key Contacts

| Role | Name | Email | Phone | Notes |
|------|------|-------|-------|-------|
| Account Manager | [Name] | [email] | [phone] | [timezone, availability] |
| Support Contact | [Name] | [email] | [phone] | [24/7? Business hours?] |
| Escalation | [Name] | [email] | [phone] | [When to escalate] |

## Contract Terms

**Contract Start Date**: [YYYY-MM-DD]  
**Contract End Date**: [YYYY-MM-DD]  
**Duration**: [X years]  

**Renewal**:
- Auto-renews: [Yes/No]
- Renewal notice required: [X days before expiry]
- Notice deadline: [YYYY-MM-DD]

**Cost**:
- Annual cost: $[amount]
- Payment schedule: [Monthly/Annual/other]
- Cost per user/seat: $[if applicable]
- Price lock expires: [date, if applicable]

**Key Terms**:
- Data residency: [location]
- Cancellation penalty: [terms]
- Service level: [describe]

## SLA & Performance Metrics

**Uptime SLA**: [X]% (typically 99.5%, 99.9%, etc.)  
**Support Response Time**: [X hours for priority, X hours for normal]  
**Support Availability**: [24/7, Business hours, Timezone]

**Last 6 Months Performance**:
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Uptime % | [target]% | [actual]% | ✓ |
| Support response time | [target] hrs | [actual] hrs | ✓ |
| Critical incidents | 0 | [actual] | [status] |
| Overall satisfaction | [score] | [actual] | [status] |

**Performance Score**: [0-100] (updated [YYYY-MM-DD])

## Performance Notes

**Strengths**:
- [What they do well]
- [Reliability/responsiveness]

**Weaknesses**:
- [Pain points]
- [Feature gaps]
- [Support issues]

**Recent Issues**:
- [YYYY-MM-DD]: [Incident description] — [Resolution]
- [YYYY-MM-DD]: [Incident description] — [Resolution]

**Relationship Quality**: [Excellent/Good/Fair/Poor]

## Renewal Status

**Days Until Expiry**: [X days]  
**Renewal Decision Needed By**: [YYYY-MM-DD]  
**Status**: [Active/Renewal-Due/At-Risk]

**Renewal Recommendation**: [Renew/Replace/Renegotiate/Monitor]

**Reasons for recommendation**:
- [Key factor 1]
- [Key factor 2]
- [Key factor 3]

## Alternatives Considered

| Vendor | Service | Cost/year | Key Features | Pros | Cons |
|--------|---------|-----------|--------------|------|------|
| [Current] | [Service] | $[X] | [Features] | [+] | [-] |
| [Alt 1] | [Service] | $[X] | [Features] | [+] | [-] |
| [Alt 2] | [Service] | $[X] | [Features] | [+] | [-] |

**Recommended alternative (if not renewing)**: [Vendor name] — [Why]

## Review History

**Last Review**: [YYYY-MM-DD] by [Reviewer]  
**Decision**: [Renewed/Replaced/Renegotiated/To-be-decided]

---

[[ops/vendors]] | Updated: [YYYY-MM-DD]
```

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
