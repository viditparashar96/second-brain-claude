#!/usr/bin/env python3
"""
Second Brain MCP Server — Full-featured MCP server for both Claude Code and Claude Desktop.

For Claude Code: Used via .mcp.json in the plugin
For Claude Desktop: Configured in ~/Library/Application Support/Claude/claude_desktop_config.json

Features:
  Tools:     16 tools (search, email, tasks, PRs, vault management)
  Resources: SOUL.md, USER.md, MEMORY.md, HABITS.md (auto-loaded into every conversation)
  Prompts:   Pre-built workflows (draft email, review PR, meeting notes, status check)
"""

import json
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

from mcp.server.fastmcp import FastMCP

from config import VAULT_DIR, DAILY_DIR, DB_PATH, SECOND_BRAIN_HOME, load_config, is_setup_complete

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


# ═══════════════════════════════════════════════════════════════════
# TOOLS — Same as before, available in both Claude Code and Desktop
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
    """Create a file in the vault. Types: project, client, team, research, content, meeting.

    Example: create_vault_file("project", "School Cab", "Uber-like app for school students")
    """
    import re
    type_map = {
        "project": VAULT_DIR / "projects",
        "client": VAULT_DIR / "clients",
        "team": VAULT_DIR / "team",
        "research": VAULT_DIR / "research",
        "content": VAULT_DIR / "content",
        "meeting": VAULT_DIR / "meetings",
    }

    target_dir = type_map.get(file_type)
    if not target_dir:
        return f"Unknown type: {file_type}. Use: project, client, team, research, content, meeting"

    slug = re.sub(r'[^a-z0-9\s-]', '', name.lower().strip())
    slug = re.sub(r'[\s]+', '-', slug).strip('-')[:50]

    if file_type == "meeting":
        slug = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}"

    file_path = target_dir / f"{slug}.md"
    if file_path.exists():
        return f"File already exists: {file_type}/{slug}.md"

    target_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    file_content = f"# {name}\n\n**Created:** {today}\n\n{content_text}\n"
    file_path.write_text(file_content)

    return f"Created: {file_type}/{slug}.md"


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
    mcp.run(transport="stdio")
