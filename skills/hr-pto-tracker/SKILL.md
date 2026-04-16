---
name: hr-pto-tracker
description: Log and track PTO requests, check team availability, flag coverage gaps
argument-hint: "[log|check|summary] [name] [dates]"
triggers:
  - "PTO tracker"
  - "log PTO"
  - "time off"
  - "vacation request"
  - "who's out"
  - "team availability"
  - "coverage gap"
---

# PTO Tracker

Log and track PTO (paid time off) and leave requests. Check upcoming availability, generate team summaries, and flag coverage gaps when multiple team members are out simultaneously.

## When to Trigger

- Employee requests PTO
- Manager asks "who's out this week?"
- Need to check team coverage for a period
- Planning projects and need to know availability
- Someone mentions vacation, sick day, or leave

## Workflow

### Command: Log PTO

**Syntax:** `/second-brain:pto-tracker log [name] [start-date] [end-date] [type] [reason]`

Usage: Employee or manager logs a PTO request.

**Inputs:**
- **Name** — Employee name (matches `team/{name}.md`)
- **Start date** — YYYY-MM-DD (first day out)
- **End date** — YYYY-MM-DD (last day out)
- **Type** — vacation | sick | parental | sabbatical | other
- **Reason** (optional) — Details for context (e.g., "family visit to India", "medical procedure")

**Step-by-step:**

1. Validate employee exists in vault:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{name}" --top-k 1
   ```

2. Check for conflicts (another person already PTO those dates):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "{start-date} {end-date} out of office" --top-k 3
   ```

3. Log to employee's PTO file: `~/.second-brain/vault/hr/pto/YYYY-<name-slug>.md`

   **File format:**
   ```markdown
   # PTO Log: {Name} — {Year}

   **Employee:** [[team/{Name}]]
   **Year:** YYYY
   **Total Days Used:** {N} / {Annual allocation}

   ---

   ## PTO Entries

   | Start Date | End Date | Days | Type | Reason | Approved |
   |------------|----------|------|------|--------|----------|
   | YYYY-MM-DD | YYYY-MM-DD | {N} | {Type} | {Reason} | ✓ / ✗ |
   ```

4. Cross-reference calendar (if connected):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/integrations/query.py" gcal create-event --title "OUT OF OFFICE: {Name}" --all-day --date-range "{start-date}" "{end-date}" --calendar "{name}@company.com"
   ```

5. Check for coverage gaps:
   - If 2+ people on same team out at same time → FLAG
   - If critical role (tech lead, manager, sole owner) out → FLAG
   - Display: "⚠️ Coverage alert: {Name} + {Other} both out {dates} in {team}"

6. Log to daily:
   ```
   - **HH:MM** — PTO logged: {Name} ({type}) {start-date} to {end-date}
   ```

---

### Command: Check Availability

**Syntax:** `/second-brain:pto-tracker check [date-range or "this week" or "next month"]`

Usage: See who's out during a specific period.

**Step-by-step:**

1. Parse date range (today, this week, next month, or specific dates):
   ```
   - "today" → 2026-04-14
   - "this week" → 2026-04-14 to 2026-04-20
   - "next month" → 2026-05-01 to 2026-05-31
   - "April 20-25" → 2026-04-20 to 2026-04-25
   ```

2. Search all PTO files for entries overlapping that range:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "out of office {date-range}" --top-k 10
   ```

3. Display availability matrix:

   ```markdown
   # Team Availability: {Date Range}

   ## Out of Office

   | Employee | Team | Dates | Type | Duration |
   |----------|------|-------|------|----------|
   | {Name} | {Team} | {start} – {end} | vacation | {N} days |
   | {Name2} | {Team2} | {start} – {end} | sick | {N} days |

   ## Working

   {All other team members present}

   ## Coverage Alerts

   ⚠️ {Team}: Multiple people out {dates} — {Names} unavailable
   ⚠️ {Critical person} out {dates} — coverage required

   ## Recommendations

   - {If multiple people out, suggest who might cover}
   - {If critical role out, suggest escalation plan}
   ```

4. Log to daily:
   ```
   - **HH:MM** — Availability check: {date-range} → {N} people out
   ```

---

### Command: Team Summary

**Syntax:** `/second-brain:pto-tracker summary [department or "all"] [num-months]`

Usage: Get overview of team PTO patterns, burndown, capacity.

**Step-by-step:**

1. Gather all PTO files for the department (or all departments):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/memory_search.py" "PTO Log" --top-k {team-size * 2}
   ```

2. Aggregate by employee and month:

   ```markdown
   # PTO Summary: {Department} — {Period}

   **Period:** {Start month} – {End month}

   ## By Employee

   | Employee | Vacation | Sick | Other | Total Days | % of Allocation |
   |----------|----------|------|-------|------------|-----------------|
   | {Name} | {N} | {N} | {N} | {N} | {%} |
   | {Name2} | {N} | {N} | {N} | {N} | {%} |

   **Total Days Used:** {N} / {N} available

   ## By Month

   | Month | People Out | Busiest Day |
   |-------|-----------|-------------|
   | {Month} | {N} | {dates with most people} |

   ## Patterns

   - Peak PTO periods: {dates, usually summer/holidays}
   - Individuals below quota: {Names who haven't taken full PTO}
   - Recommended time off (wellness): {Names to encourage to take PTO}

   ## Coverage Gaps

   {List any critical gaps already identified — tech lead, manager, etc.}

   ## Recommendations

   - {If someone hasn't taken PTO, suggest they plan time}
   - {If peak periods cluster, suggest staggering}
   - {If coverage gaps exist, suggest hiring or cross-training}
   ```

3. Log to daily:
   ```
   - **HH:MM** — PTO summary: {department} {period} — {total} days used, {gaps count} coverage gaps
   ```

---

## File Structure

PTO entries live in `~/.second-brain/vault/hr/pto/`:

- One file per person per year: `YYYY-<name-slug>.md`
- Example: `2026-sarah-chen.md`, `2025-michael-rodriguez.md`

**File naming:** `YYYY-<first-last-lowercase>.md`

---

## Calendar Integration

If Google Calendar is connected, PTO events should:
- Be marked "Out of Office" (not "Busy")
- Block all-day slots
- Include type (vacation, sick, etc.) in title
- Appear on employee's shared calendar so team sees them

---

## Conflict Detection

**Flags to raise:**

1. **Coverage gap** — Role owner is out and no backup
2. **Multiple people out** — If 2+ from same team simultaneously
3. **Unexplained absence** — Log entry missing (should be proactive)
4. **Exceeds quota** — Employee using more than annual allocation (unless approved exception)
5. **Cluster PTO** — Peak periods (December, summer) have too many people out

---

## Rules

- **Manager approval required** — Employee logs request; manager (or HR) must approve before marking as vacation
- **Calendar sync** — If connected, automatically create calendar events marked "Out of Office"
- **Coverage responsibility** — Manager should ensure coverage before approving PTO for critical roles
- **Transparency** — Team should be able to see who's out (shared calendars or team availability page)
- **Advanced notice** — Recommend 2+ weeks notice for vacation; urgent sick leave is understood
- **Quota tracking** — Annual PTO allocation should be tracked; unusable days roll over per policy
- **Parental/extended leave** — Handle separately if duration > 5 days; may require HR involvement
- **Cross-timezone** — If team is distributed, clarify timezone for "out of office" dates
- **Conflicts** — Prevent more than {N}% of team from being out simultaneously during critical periods

- **Cloud memory:** After completing this workflow, call the `log_note` MCP tool with a one-line summary of what was done. Example: `log_note("Completed eng-plan for School Cab — 9 phases, 22 days")`
