#!/usr/bin/env python3
"""
Second Brain MCP Server — Full-featured MCP server for both Claude Code and Claude Desktop.

For Claude Code: Used via .mcp.json in the plugin
For Claude Desktop: Configured in ~/Library/Application Support/Claude/claude_desktop_config.json

Features:
  Tools:     18 tools (search, email, tasks, PRs, vault management, department files)
  Resources: SOUL.md, USER.md, MEMORY.md, HABITS.md (auto-loaded into every conversation)
  Prompts:   Pre-built workflows across all departments (HR, Sales, Product, Ops, Engineering)
             All prompts include memory-baking: Claude auto-logs outcomes via log_note
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add scripts to path
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR / "integrations"))

# Setup logging for debugging startup failures
_sb_home = Path(os.environ.get("SECOND_BRAIN_HOME", Path.home() / ".second-brain"))
_log_dir = _sb_home / "data" / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(_log_dir / "mcp-server.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("second-brain-mcp")

try:
    # IMPORTANT: Activate venv BEFORE importing any third-party packages (mcp, dotenv, etc.)
    # config.py calls ensure_deps.activate() which adds ~/.second-brain/.venv/site-packages to sys.path
    from config import VAULT_DIR, DAILY_DIR, DB_PATH, SECOND_BRAIN_HOME, load_config, is_setup_complete
    logger.info("config.py loaded successfully")
except Exception as e:
    logger.error(f"Failed to import config: {e}", exc_info=True)
    raise

try:
    from mcp.server.fastmcp import FastMCP
    logger.info("mcp package loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import mcp package: {e}")
    logger.error("Hint: Ensure the venv exists and has 'mcp' installed.")
    logger.error(f"  Venv path: {_sb_home / '.venv'}")
    logger.error(f"  Try: {_sb_home / '.venv' / 'bin' / 'pip'} install mcp")
    raise

mcp = FastMCP("Second Brain")


def _run_query(*args, timeout=30) -> str:
    """Run a query.py subcommand and return stdout."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "integrations" / "query.py"), *args],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(PLUGIN_ROOT),
            env={**os.environ, "SECOND_BRAIN_HOME": str(SECOND_BRAIN_HOME)},
        )
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"


# ═══════════════════════════════════════════════════════════════════
# RESOURCES — Auto-loaded into every Claude Desktop conversation
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("second-brain://soul")
def get_soul() -> str:
    """Agent personality and behavioral rules."""
    path = VAULT_DIR / "SOUL.md"
    return path.read_text() if path.exists() else "SOUL.md not found. Run setup first."


@mcp.resource("second-brain://user")
def get_user_profile() -> str:
    """User profile, accounts, team, and preferences."""
    path = VAULT_DIR / "USER.md"
    return path.read_text() if path.exists() else "USER.md not found. Run setup first."


@mcp.resource("second-brain://org")
def get_org() -> str:
    """Organization profile — company info, departments, strategic goals."""
    path = VAULT_DIR / "ORG.md"
    return path.read_text() if path.exists() else "ORG.md not found. Run /second-brain:setup to configure your organization."


@mcp.resource("second-brain://products")
def get_products() -> str:
    """Product registry — all organization products with context for every department."""
    path = VAULT_DIR / "PRODUCTS.md"
    return path.read_text() if path.exists() else "PRODUCTS.md not found. Use /second-brain:product-manager to add your products."


@mcp.resource("second-brain://memory")
def get_memory() -> str:
    """Long-term knowledge — decisions, projects, clients, lessons, goals."""
    path = VAULT_DIR / "MEMORY.md"
    return path.read_text() if path.exists() else "MEMORY.md not found. Run setup first."


@mcp.resource("second-brain://habits")
def get_habits() -> str:
    """Daily improvement pillars and tracking."""
    path = VAULT_DIR / "HABITS.md"
    return path.read_text() if path.exists() else "HABITS.md not found. Run setup first."


@mcp.resource("second-brain://today")
def get_today_log() -> str:
    """Today's daily log — real-time activity feed."""
    today = datetime.now().strftime("%Y-%m-%d")
    path = DAILY_DIR / f"{today}.md"
    return path.read_text() if path.exists() else f"No daily log for {today} yet."


# ═══════════════════════════════════════════════════════════════════
# PROMPTS — Pre-built workflows for Claude Desktop users
# ═══════════════════════════════════════════════════════════════════

@mcp.prompt()
def status_check() -> str:
    """Get a quick status overview of all connected integrations, tasks, and emails."""
    return """Check all my connected integrations and give me a status overview:
1. Use the get_status tool to see which integrations are connected
2. If Gmail is connected, use list_emails with unread_only=true to show unread count
3. If Asana is connected, use overdue_tasks and upcoming_tasks to show deadlines
4. Summarize everything grouped by priority: urgent / today / this week"""


@mcp.prompt()
def draft_email(recipient: str = "", context: str = "") -> str:
    """Draft an email in your voice."""
    return f"""Draft an email for me:
Recipient: {recipient or '[ask me who to send to]'}
Context: {context or '[ask me what the email is about]'}

Steps:
1. Search my memory for context about the recipient using search_memory
2. Search drafts/sent for my past emails using search_memory with path_prefix='drafts/sent'
3. Draft the email matching my communication style (direct, concise, professional)
4. Use the draft_email tool to create a Gmail draft — NEVER send
5. Log what you drafted using log_note"""


@mcp.prompt()
def review_pr(repo: str = "", pr_number: str = "") -> str:
    """Do an initial code review sweep on a GitHub PR."""
    return f"""Review this pull request:
Repo: {repo or '[ask me which repo]'}
PR: {pr_number or '[ask me which PR number]'}

Steps:
1. Use pr_diff to get the file changes
2. Analyze each file for: correctness, edge cases, security issues, missing tests
3. Be constructive — suggest fixes, not just problems
4. Skip style nits, focus on logic and security
5. Log the review summary using log_note"""


@mcp.prompt()
def meeting_notes(topic: str = "", attendees: str = "") -> str:
    """Capture and organize meeting notes."""
    return f"""Help me capture meeting notes:
Topic: {topic or '[ask me what the meeting was about]'}
Attendees: {attendees or '[ask me who attended]'}

Structure the notes as:
- Date, time, attendees
- Agenda items discussed
- Key decisions made (who decided what, why)
- Action items (who, what, by when)

Save to the vault using log_note for now. Include [[wiki-links]] for people and projects mentioned."""


@mcp.prompt()
def catch_me_up() -> str:
    """Summarize what happened recently — emails, tasks, and vault activity."""
    return """Catch me up on everything:
1. Use list_emails with unread_only=true to show recent unread emails
2. Use overdue_tasks to show what's overdue
3. Use upcoming_tasks to show what's coming up this week
4. Use search_memory with query='today' to find recent vault activity
5. Summarize by priority: what needs immediate attention, what can wait"""


@mcp.prompt()
def search_knowledge(query: str = "") -> str:
    """Search your Second Brain vault for past decisions, notes, and context."""
    return f"""Search my knowledge base:
Query: {query or '[ask me what to search for]'}

Use search_memory with the query. If results are found, summarize the key findings.
If not found, suggest what I might search for instead."""


# ─── HR Prompts ──────────────────────────────────────────────────

@mcp.prompt()
def interview_feedback(candidate: str = "", role: str = "") -> str:
    """Structure interview feedback into a consistent scorecard."""
    return f"""Help me structure interview feedback:
Candidate: {candidate or '[ask me the candidate name]'}
Role: {role or '[ask me what role they interviewed for]'}

Steps:
1. Ask me to paste or describe the raw interview notes
2. Search memory for the role requirements using search_memory with the role name
3. Structure into a scorecard: candidate info, competency ratings (Technical Skills, Communication, Problem Solving, Culture Fit — rate 1-5), strengths, concerns, hiring recommendation
4. Save the scorecard using create_vault_file with type 'hr-interview'
5. Ask if I want to create an Asana follow-up task for the hiring decision using create_task
6. IMPORTANT: Log the outcome using log_note — e.g. 'Interview feedback captured for [candidate] for [role] — recommendation: [hire/no-hire/maybe]'"""


@mcp.prompt()
def onboarding_plan(new_hire: str = "", role: str = "", start_date: str = "") -> str:
    """Generate a role-specific onboarding checklist for a new hire."""
    return f"""Create an onboarding plan:
New hire: {new_hire or '[ask me their name]'}
Role: {role or '[ask me their role]'}
Start date: {start_date or '[ask me when they start]'}

Steps:
1. Search memory for team context and project info using search_memory
2. Generate a phased onboarding checklist: Pre-arrival (IT setup, accounts, workspace), Week 1 (orientation, tools, buddy), Month 1 (training, first tasks), 30-60-90 day goals
3. Save using create_vault_file with type 'hr-onboarding'
4. Create a team profile for the new hire using create_vault_file with type 'team'
5. Ask if I want to create Asana tasks for each onboarding phase using create_task
6. IMPORTANT: Log using log_note — e.g. 'Onboarding plan created for [name], [role], starting [date]'"""


@mcp.prompt()
def performance_review_prep(employee: str = "", period: str = "") -> str:
    """Gather context and draft a performance review."""
    return f"""Prep a performance review:
Employee: {employee or '[ask me who]'}
Review period: {period or '[ask me the time period]'}

Steps:
1. Search memory for the employee's contributions, meeting mentions, and project work using search_memory
2. Check vault for their team profile using read_vault_file
3. Pull their task completions from Asana using list_tasks
4. Draft a structured review: accomplishments, areas of growth, goal progress, recommended next-period goals
5. Save using create_vault_file with type 'hr-review'
6. IMPORTANT: Log using log_note — e.g. 'Performance review draft prepared for [employee] — period: [period]'
7. Remind me this is a DRAFT that needs my review before sharing"""


@mcp.prompt()
def policy_lookup(question: str = "") -> str:
    """Search company policies and answer HR questions."""
    return f"""Answer this policy question:
Question: {question or '[ask me what I want to know]'}

Steps:
1. Search memory for relevant policies using search_memory with path_prefix='hr/policies'
2. Also search broader vault context using search_memory
3. If a matching policy exists, answer with specific citations and references
4. If NO policy is found, clearly state that — NEVER make up policies
5. Offer to draft a new policy if one is needed, saving with create_vault_file type 'hr-policy'
6. IMPORTANT: Log the query using log_note — e.g. 'Policy lookup: [question] — [found/not found]'"""


# ─── Sales Prompts ───────────────────────────────────────────────

@mcp.prompt()
def deal_prep(client: str = "") -> str:
    """Prepare a pre-meeting brief for a client or prospect call."""
    return f"""Prep me for a client meeting:
Client: {client or '[ask me which client/prospect]'}

Steps:
1. Search memory for client context using search_memory
2. Search Gmail for recent emails with this client using search_emails
3. Check vault for their client file using read_vault_file in clients/
4. Check Asana for open tasks related to this client using list_tasks
5. Generate a brief: client background, relationship history, last interaction, open items, talking points, goals for the call
6. Save the brief using create_vault_file with type 'sales-brief'
7. IMPORTANT: Log using log_note — e.g. 'Deal prep brief created for [client] meeting'"""


@mcp.prompt()
def draft_proposal(client: str = "", scope: str = "") -> str:
    """Draft a client proposal."""
    return f"""Draft a proposal:
Client: {client or '[ask me which client]'}
Scope: {scope or '[ask me about the project scope]'}

Steps:
1. Search memory for client history and similar past proposals using search_memory
2. Pull client context from vault using read_vault_file
3. Search past emails for communication tone using search_emails
4. Draft a structured proposal: executive summary, scope, deliverables, timeline, investment, terms, next steps
5. Save using create_vault_file with type 'sales-proposal'
6. Ask if I want to create a Gmail draft to send it using draft_email
7. IMPORTANT: Log using log_note — e.g. 'Proposal drafted for [client] — scope: [summary]'"""


@mcp.prompt()
def pipeline_review() -> str:
    """Review the sales deal pipeline."""
    return """Review my deal pipeline:

Steps:
1. Pull active deals from Asana using list_tasks (look for sales-related projects)
2. Cross-reference with vault client files using search_memory
3. Check email recency for each deal using search_emails
4. Generate a pipeline summary: deals by stage, stale deals (no activity >7 days), upcoming deadlines, at-risk opportunities
5. Save snapshot using create_vault_file with type 'sales-pipeline'
6. Highlight what needs immediate action
7. IMPORTANT: Log using log_note — e.g. 'Pipeline review: [N] active deals, [N] at risk, [N] stale'"""


# ─── Product/Management Prompts ──────────────────────────────────

@mcp.prompt()
def draft_prd(feature: str = "") -> str:
    """Create a Product Requirements Document from rough notes."""
    return f"""Help me write a PRD:
Feature/product: {feature or '[ask me what feature or product]'}

Steps:
1. Ask me for rough notes, user feedback, or a description of the problem
2. Search memory for related discussions and past decisions using search_memory
3. Pull project context from vault using read_vault_file
4. Generate a structured PRD: problem statement, goals & success metrics, user stories, functional requirements, non-functional requirements, open questions, out of scope, timeline estimate
5. Save using create_vault_file with type 'product-prd'
6. Ask if I want to create Asana tasks for the key milestones using create_task
7. IMPORTANT: Log using log_note — e.g. 'PRD drafted for [feature] — [key goal summary]'"""


@mcp.prompt()
def okr_update(period: str = "") -> str:
    """Check or update OKR progress."""
    return f"""Review OKR progress:
Period: {period or 'current quarter'}

Steps:
1. Search vault for existing OKRs using search_memory with path_prefix='product/okrs'
2. If found, pull the OKR file using read_vault_file
3. Check Asana for completed tasks that map to key results using list_tasks
4. Update progress percentages and status (on-track / at-risk / behind)
5. Save updated OKRs using create_vault_file with type 'product-okr'
6. Flag any at-risk objectives that need attention
7. IMPORTANT: Log using log_note — e.g. 'OKR review: [N] on track, [N] at risk, [N] behind'"""


@mcp.prompt()
def one_on_one_prep(team_member: str = "") -> str:
    """Prepare talking points for a 1:1 meeting."""
    return f"""Prep for my 1:1:
Team member: {team_member or '[ask me who]'}

Steps:
1. Search vault for their team profile using read_vault_file in team/
2. Search for past 1:1 notes using search_memory with query '[name] 1:1'
3. Check Asana for their open and overdue tasks using list_tasks
4. Search daily logs for recent mentions of this person using search_memory
5. Generate talking points: open action items from last 1:1, recent wins, blockers to discuss, growth/career topics
6. After the 1:1, help me capture notes and save using create_vault_file with type 'meeting'
7. IMPORTANT: Log using log_note — e.g. '1:1 prep done for [name] — [key topics]'"""


@mcp.prompt()
def stakeholder_update(period: str = "", audience: str = "") -> str:
    """Generate a status update by synthesizing recent activity."""
    return f"""Write a status update:
Period: {period or '[ask me: this week, last week, this month]'}
Audience: {audience or '[ask me: team, leadership, or client]'}

Steps:
1. Pull daily logs for the period using search_memory
2. Check Asana for completed tasks using list_tasks
3. Search for key decisions and wins in memory using search_memory
4. Synthesize into: highlights/wins, progress on goals, blockers/risks, upcoming priorities, asks/decisions needed
5. Adapt tone to audience (casual for team, metrics-focused for leadership, polished for clients)
6. Save using create_vault_file with type 'product-update'
7. Ask if I want to send as email using draft_email
8. IMPORTANT: Log using log_note — e.g. '[audience] update generated for [period] — [key highlight]'"""


# ─── Operations Prompts ──────────────────────────────────────────

@mcp.prompt()
def create_sop(process_name: str = "") -> str:
    """Create or update a Standard Operating Procedure."""
    return f"""Help me document an SOP:
Process: {process_name or '[ask me which process]'}

Steps:
1. Ask me to describe the process steps, or paste existing documentation
2. Search memory for related SOPs and processes using search_memory with path_prefix='ops/sops'
3. Structure into: purpose, scope, roles & responsibilities, step-by-step procedure with decision points, tools required, exception handling, review schedule
4. Save using create_vault_file with type 'ops-sop'
5. IMPORTANT: Log using log_note — e.g. 'SOP created/updated: [process name] — owner: [owner]'"""


@mcp.prompt()
def compliance_check(framework: str = "") -> str:
    """Run a compliance audit or check compliance status."""
    return f"""Check compliance status:
Framework: {framework or '[ask me: SOC 2, GDPR, HIPAA, ISO 27001, or custom]'}

Steps:
1. Search vault for existing compliance checklists using search_memory with path_prefix='ops/compliance'
2. If found, review current status of each requirement
3. If not found, help me create a new checklist for this framework
4. Generate a compliance dashboard: overall score, compliant items, non-compliant items, items in progress, overdue reviews
5. For non-compliant items, ask if I want to create Asana tasks using create_task
6. Save using create_vault_file with type 'ops-compliance'
7. IMPORTANT: Log using log_note — e.g. 'Compliance check [{framework}]: [score]% compliant, [N] items need attention'"""


@mcp.prompt()
def process_audit(process_area: str = "") -> str:
    """Audit an operational process for bottlenecks and improvements."""
    return f"""Audit this process:
Area: {process_area or '[ask me which process or area]'}

Steps:
1. Search vault for related SOPs using search_memory with path_prefix='ops/sops'
2. Search daily logs for mentions of issues or bottlenecks using search_memory
3. Search Gmail for complaints or escalations using search_emails
4. Generate an audit report: current state, bottlenecks identified, improvement recommendations ranked by impact, implementation plan
5. Save using create_vault_file with type 'ops-audit'
6. Ask if I want to create Asana tasks for the top recommendations using create_task
7. IMPORTANT: Log using log_note — e.g. 'Process audit: [area] — [N] bottlenecks found, top recommendation: [summary]'"""


# ─── Organization & Product Prompts ──────────────────────────────

@mcp.prompt()
def manage_products(action: str = "") -> str:
    """Add, update, or list products in the organization's product registry."""
    return f"""Manage the product registry:
Action: {action or '[ask me: add, update, list, or remove]'}

The product registry (PRODUCTS.md) is the single source of truth for all organization products.
Every department skill pulls from this file.

Steps:
1. Read the current PRODUCTS.md using read_vault_file with path 'PRODUCTS.md'
2. For 'add': Ask me for product details (name, category, status, target audience, description, key features, tech stack, pricing, competitive edge, key clients, known issues, roadmap). Then add the entry to PRODUCTS.md.
3. For 'update': Find the product by name, ask what changed, update the entry.
4. For 'list': Show all products grouped by status (active, in development, sunset) with a 1-liner each.
5. For 'remove': Move to Sunset section with date and reason — never delete.
6. IMPORTANT: Log using log_note — e.g. 'Product registry updated: [action] [product name]'"""


@mcp.prompt()
def setup_org(org_name: str = "") -> str:
    """Set up or update the organization profile."""
    return f"""Set up the organization profile:
Organization: {org_name or '[ask me the company name]'}

Steps:
1. Ask me for: company name, industry, HQ, website, description, departments, team structure, strategic goals
2. Check if ORG.md already exists using read_vault_file with path 'ORG.md'
3. Create or update ORG.md with the collected information
4. After setting up ORG.md, ask if I want to add products using the manage_products prompt
5. IMPORTANT: Log using log_note — e.g. 'Organization profile created/updated: [org name]'"""


# ═══════════════════════════════════════════════════════════════════
# TOOLS — Available in both Claude Code and Desktop
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def search_memory(query: str, top_k: int = 5, path_prefix: str = "") -> str:
    """Search the memory vault using hybrid RAG (vector + keyword). Find past decisions, meeting notes, client info, project context."""
    try:
        from db import MemoryDB
        from embeddings import embed_query as _embed_query

        if not Path(DB_PATH).exists():
            return "Memory index not built yet. Run index_vault first."

        db = MemoryDB()
        query_emb = _embed_query(query)
        fetch_k = top_k * 3

        vec_results = db.vector_search(query_emb, top_k=fetch_k, path_prefix=path_prefix)
        kw_results = db.keyword_search(query, top_k=fetch_k, path_prefix=path_prefix)

        merged = {}
        for r in vec_results:
            merged[r["id"]] = {**r, "vec_score": r["score"], "kw_score": 0.0}
        for r in kw_results:
            if r["id"] in merged:
                merged[r["id"]]["kw_score"] = r["score"]
            else:
                merged[r["id"]] = {**r, "vec_score": 0.0, "kw_score": r["score"]}

        for item in merged.values():
            item["score"] = 0.7 * item["vec_score"] + 0.3 * item["kw_score"]

        ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:top_k]
        db.close()

        if not ranked:
            return "No results found."

        lines = []
        for i, r in enumerate(ranked, 1):
            lines.append(f"[{i}] {r['file_path']} > {r['heading_path']}  (score: {r['score']:.3f})")
            lines.append(r["content"][:300])
            lines.append("")
        return "\n".join(lines)

    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def log_note(note: str) -> str:
    """Save a note to today's daily vault log. Use for decisions, action items, meeting summaries."""
    try:
        DAILY_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = DAILY_DIR / f"{today}.md"
        now = datetime.now().strftime("%H:%M")

        entry = f"- **{now}** — {note}\n"

        if log_path.exists():
            content = log_path.read_text()
            if not content.endswith("\n"):
                entry = "\n" + entry
        else:
            entry = f"# Daily Log — {today}\n\n## Log\n\n" + entry

        with open(log_path, "a") as f:
            f.write(entry)

        return f"Logged to {today}.md"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def index_vault() -> str:
    """Re-index the vault for search. Run after adding new files."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "memory_index.py")],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "SECOND_BRAIN_HOME": str(SECOND_BRAIN_HOME)},
        )
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def create_vault_file(file_type: str, name: str, content_text: str) -> str:
    """Create a file in the vault.

    Types: project, client, team, research, content, meeting,
           hr-interview, hr-onboarding, hr-review, hr-policy, hr-pto,
           sales-brief, sales-proposal, sales-follow-up, sales-competitor, sales-pipeline,
           product-prd, product-okr, product-update, product-feedback,
           ops-sop, ops-vendor, ops-compliance, ops-audit, ops-allocation

    Example: create_vault_file("project", "School Cab", "Uber-like app for school students")
    Example: create_vault_file("hr-interview", "John Doe", "Interview scorecard content")
    Example: create_vault_file("sales-proposal", "Acme Corp", "Proposal content")
    """
    import re
    type_map = {
        # Core
        "project": VAULT_DIR / "projects",
        "client": VAULT_DIR / "clients",
        "team": VAULT_DIR / "team",
        "research": VAULT_DIR / "research",
        "content": VAULT_DIR / "content",
        "meeting": VAULT_DIR / "meetings",
        # HR
        "hr-interview": VAULT_DIR / "hr" / "interviews",
        "hr-onboarding": VAULT_DIR / "hr" / "onboarding",
        "hr-review": VAULT_DIR / "hr" / "reviews",
        "hr-policy": VAULT_DIR / "hr" / "policies",
        "hr-pto": VAULT_DIR / "hr" / "pto",
        # Sales
        "sales-brief": VAULT_DIR / "sales" / "briefs",
        "sales-proposal": VAULT_DIR / "sales" / "proposals",
        "sales-follow-up": VAULT_DIR / "sales" / "follow-ups",
        "sales-competitor": VAULT_DIR / "sales" / "competitors",
        "sales-pipeline": VAULT_DIR / "sales" / "pipeline",
        # Product
        "product-prd": VAULT_DIR / "product" / "prds",
        "product-okr": VAULT_DIR / "product" / "okrs",
        "product-update": VAULT_DIR / "product" / "updates",
        "product-feedback": VAULT_DIR / "product" / "feedback",
        # Ops
        "ops-sop": VAULT_DIR / "ops" / "sops",
        "ops-vendor": VAULT_DIR / "ops" / "vendors",
        "ops-compliance": VAULT_DIR / "ops" / "compliance",
        "ops-audit": VAULT_DIR / "ops" / "audits",
        "ops-allocation": VAULT_DIR / "ops" / "allocation",
    }

    target_dir = type_map.get(file_type)
    if not target_dir:
        valid = ", ".join(sorted(type_map.keys()))
        return f"Unknown type: {file_type}. Valid types: {valid}"

    slug = re.sub(r'[^a-z0-9\s-]', '', name.lower().strip())
    slug = re.sub(r'[\s]+', '-', slug).strip('-')[:50]

    # Date-prefixed types
    date_prefixed = {"meeting", "hr-interview", "hr-onboarding", "hr-review",
                     "sales-brief", "sales-proposal", "sales-follow-up", "sales-pipeline",
                     "product-prd", "product-update", "product-feedback",
                     "ops-audit", "ops-allocation"}
    if file_type in date_prefixed:
        slug = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}"

    file_path = target_dir / f"{slug}.md"
    if file_path.exists():
        return f"File already exists: {file_type}/{slug}.md"

    target_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    file_content = f"# {name}\n\n**Created:** {today}\n\n{content_text}\n"
    file_path.write_text(file_content)

    return f"Created: {file_type}/{slug}.md"


@mcp.tool()
def read_vault_file(file_path: str) -> str:
    """Read a file from the vault by relative path. Example: read_vault_file('hr/policies/remote-work.md')"""
    target = VAULT_DIR / file_path
    if not target.exists():
        return f"File not found: {file_path}"
    if not str(target.resolve()).startswith(str(VAULT_DIR.resolve())):
        return "Access denied: path must be inside the vault."
    return target.read_text()


@mcp.tool()
def list_vault_dir(dir_path: str = "") -> str:
    """List files in a vault directory. Example: list_vault_dir('hr/interviews') or list_vault_dir('sales/proposals')"""
    target = VAULT_DIR / dir_path if dir_path else VAULT_DIR
    if not target.exists():
        return f"Directory not found: {dir_path or 'vault root'}"
    if not target.is_dir():
        return f"Not a directory: {dir_path}"
    if not str(target.resolve()).startswith(str(VAULT_DIR.resolve())):
        return "Access denied: path must be inside the vault."

    items = sorted(target.iterdir())
    lines = []
    for item in items:
        prefix = "📁" if item.is_dir() else "📄"
        rel = item.relative_to(VAULT_DIR)
        lines.append(f"{prefix} {rel}")
    return "\n".join(lines) if lines else "Empty directory."


# ─── Gmail Tools ─────────────────────────────────────────────────

@mcp.tool()
def list_emails(unread_only: bool = False, limit: int = 10) -> str:
    """List recent emails from Gmail."""
    args = ["gmail", "list", "--limit", str(limit)]
    if unread_only:
        args.append("--unread")
    return _run_query(*args)


@mcp.tool()
def read_email(message_id: str) -> str:
    """Read a specific email by its Gmail message ID."""
    return _run_query("gmail", "read", message_id)


@mcp.tool()
def draft_email(to: str, subject: str, body: str) -> str:
    """Create a Gmail draft (never sends). For composing emails for review."""
    return _run_query("gmail", "draft", "--to", to, "--subject", subject, "--body", body)


@mcp.tool()
def search_emails(gmail_query: str, limit: int = 10) -> str:
    """Search Gmail with query syntax (e.g. 'from:boss@co.com')."""
    return _run_query("gmail", "search", gmail_query, "--limit", str(limit))


# ─── Asana Tools ─────────────────────────────────────────────────

@mcp.tool()
def list_tasks(project_gid: str = "") -> str:
    """List Asana tasks. Optionally filter by project GID."""
    args = ["asana", "tasks"]
    if project_gid:
        args.extend(["--project", project_gid])
    return _run_query(*args)


@mcp.tool()
def overdue_tasks() -> str:
    """Show overdue Asana tasks."""
    return _run_query("asana", "overdue")


@mcp.tool()
def upcoming_tasks(days: int = 7) -> str:
    """Show Asana tasks due in the next N days."""
    return _run_query("asana", "upcoming", "--days", str(days))


@mcp.tool()
def list_projects() -> str:
    """List all Asana projects."""
    return _run_query("asana", "projects")


@mcp.tool()
def create_task(name: str, due_date: str = "", notes: str = "", project_gid: str = "") -> str:
    """Create an Asana task. Useful for action items from meetings, onboarding steps, compliance items."""
    args = ["asana", "create-task", "--name", name]
    if due_date:
        args.extend(["--due", due_date])
    if notes:
        args.extend(["--notes", notes])
    if project_gid:
        args.extend(["--project", project_gid])
    return _run_query(*args)


@mcp.tool()
def calendar_events(date_range: str = "today") -> str:
    """Get calendar events. date_range: 'today', 'tomorrow', 'this-week', or 'YYYY-MM-DD'."""
    if date_range in ("today", "tomorrow", "this-week"):
        return _run_query("gcal", "events", f"--{date_range}")
    return _run_query("gcal", "events", "--date", date_range)


# ─── GitHub Tools ────────────────────────────────────────────────

@mcp.tool()
def list_prs(repo: str, state: str = "open") -> str:
    """List pull requests for a GitHub repo (owner/repo)."""
    return _run_query("github", "prs", "--repo", repo, "--state", state)


@mcp.tool()
def pr_diff(repo: str, pr_number: int) -> str:
    """Get file changes (diff) for a GitHub PR."""
    return _run_query("github", "diff", str(pr_number), "--repo", repo)


@mcp.tool()
def github_rate_limit() -> str:
    """Check GitHub API rate limit."""
    return _run_query("github", "rate-limit")


# ─── Status ──────────────────────────────────────────────────────

@mcp.tool()
def get_status() -> str:
    """Get a status overview of all connected integrations."""
    return _run_query("status")


# ═══════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("Second Brain MCP Server starting (20 tools, 20 prompts, 5 resources)")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"MCP Server crashed: {e}", exc_info=True)
        raise
