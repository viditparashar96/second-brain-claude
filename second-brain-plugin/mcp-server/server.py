#!/usr/bin/env python3
"""
Second Brain MCP Server — Exposes memory, integrations, and vault tools
to Claude Code and Claude Desktop via Model Context Protocol.

Tools:
  - search_memory: RAG search across vault
  - list_emails: Gmail inbox
  - read_email: Read specific email
  - draft_email: Create Gmail draft
  - list_tasks: Asana tasks
  - overdue_tasks: Asana overdue tasks
  - upcoming_tasks: Asana upcoming deadlines
  - list_prs: GitHub PRs
  - pr_diff: GitHub PR file changes
  - get_status: Integration status overview
  - log_note: Save a note to today's daily log
  - index_vault: Re-index vault for search
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

mcp = FastMCP("Second Brain", json_response=True)


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


# ─── Memory Tools ────────────────────────────────────────────────

@mcp.tool()
def search_memory(query: str, top_k: int = 5, path_prefix: str = "") -> str:
    """Search the memory vault using hybrid RAG (vector + keyword). Use this to find past decisions, meeting notes, client info, project context, etc."""
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
    """Save a note to today's daily vault log. Use for decisions, action items, or anything worth remembering."""
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


# ─── Gmail Tools ─────────────────────────────────────────────────

@mcp.tool()
def list_emails(unread_only: bool = False, limit: int = 10) -> str:
    """List recent emails from Gmail. Set unread_only=true for unread only."""
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
    """Create a Gmail draft (never sends). Use for composing emails for review."""
    return _run_query("gmail", "draft", "--to", to, "--subject", subject, "--body", body)


@mcp.tool()
def search_emails(gmail_query: str, limit: int = 10) -> str:
    """Search Gmail with query syntax (e.g. 'from:boss@co.com after:2025/01/01')."""
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
    """Show overdue Asana tasks (past due date, not completed)."""
    return _run_query("asana", "overdue")


@mcp.tool()
def upcoming_tasks(days: int = 7) -> str:
    """Show Asana tasks due in the next N days."""
    return _run_query("asana", "upcoming", "--days", str(days))


@mcp.tool()
def list_projects() -> str:
    """List all Asana projects in the workspace."""
    return _run_query("asana", "projects")


# ─── GitHub Tools ────────────────────────────────────────────────

@mcp.tool()
def list_prs(repo: str, state: str = "open") -> str:
    """List pull requests for a GitHub repo (owner/repo format)."""
    return _run_query("github", "prs", "--repo", repo, "--state", state)


@mcp.tool()
def pr_diff(repo: str, pr_number: int) -> str:
    """Get file changes (diff) for a GitHub pull request."""
    return _run_query("github", "diff", str(pr_number), "--repo", repo)


@mcp.tool()
def github_rate_limit() -> str:
    """Check GitHub API rate limit status."""
    return _run_query("github", "rate-limit")


# ─── Status Tool ─────────────────────────────────────────────────

@mcp.tool()
def get_status() -> str:
    """Get a quick status overview of all connected integrations."""
    return _run_query("status")


# ─── Run ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
