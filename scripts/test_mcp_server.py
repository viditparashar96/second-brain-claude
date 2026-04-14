#!/usr/bin/env python3
"""
Test script for the Second Brain MCP server.

Run this to validate:
1. Import chain works (venv activation, config, mcp package)
2. All tools are registered
3. All prompts are registered
4. All resources are registered
5. Vault directory structure is correct

Usage:
    python3 scripts/test_mcp_server.py

    # Or from the plugin root:
    SECOND_BRAIN_HOME=~/.second-brain python3 scripts/test_mcp_server.py
"""

import os
import sys
from pathlib import Path

# Setup paths exactly like the MCP server does
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR / "integrations"))

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
WARN = "\033[93m⚠\033[0m"

errors = 0
warnings = 0


def check(label, condition, warn_only=False):
    global errors, warnings
    if condition:
        print(f"  {PASS} {label}")
    elif warn_only:
        print(f"  {WARN} {label}")
        warnings += 1
    else:
        print(f"  {FAIL} {label}")
        errors += 1


# ── Step 1: Config & Venv ──────────────────────────────────────────

print("\n== Step 1: Config & Dependencies ==")

try:
    from config import (
        VAULT_DIR, DAILY_DIR, DB_PATH, SECOND_BRAIN_HOME,
        load_config, is_setup_complete, ensure_dirs
    )
    check("config.py imports successfully", True)
except Exception as e:
    check(f"config.py import failed: {e}", False)
    sys.exit(1)

check(f"SECOND_BRAIN_HOME = {SECOND_BRAIN_HOME}", SECOND_BRAIN_HOME.exists(),
      warn_only=True)
check(f"VAULT_DIR = {VAULT_DIR}", VAULT_DIR.exists(), warn_only=True)

try:
    from mcp.server.fastmcp import FastMCP
    check("mcp package importable", True)
except ImportError as e:
    check(f"mcp package NOT importable: {e}", False)
    print(f"\n  Hint: Run the setup wizard first, or manually install deps:")
    print(f"  python3 -m venv {SECOND_BRAIN_HOME / '.venv'}")
    print(f"  {SECOND_BRAIN_HOME / '.venv' / 'bin' / 'pip'} install -r {PLUGIN_ROOT / 'requirements.txt'}")
    sys.exit(1)


# ── Step 2: MCP Server Import ──────────────────────────────────────

print("\n== Step 2: MCP Server Module ==")

try:
    # Import the server module
    sys.path.insert(0, str(PLUGIN_ROOT / "mcp-server"))
    import server as mcp_server
    check("server.py imports successfully", True)
except Exception as e:
    check(f"server.py import failed: {e}", False)
    sys.exit(1)

mcp_obj = mcp_server.mcp


# ── Step 3: Tools ──────────────────────────────────────────────────

print("\n== Step 3: Registered Tools ==")

expected_tools = [
    # Core
    "search_memory", "log_note", "index_vault", "create_vault_file",
    "read_vault_file", "list_vault_dir",
    # Gmail
    "list_emails", "read_email", "draft_email", "search_emails",
    # Asana
    "list_tasks", "overdue_tasks", "upcoming_tasks", "list_projects", "create_task",
    # GitHub
    "list_prs", "pr_diff", "github_rate_limit",
    # Calendar
    "calendar_events",
    # Status
    "get_status",
]

# FastMCP stores tools internally — inspect them
registered_tools = set()
if hasattr(mcp_obj, '_tool_manager') and hasattr(mcp_obj._tool_manager, '_tools'):
    registered_tools = set(mcp_obj._tool_manager._tools.keys())
elif hasattr(mcp_obj, '_tools'):
    registered_tools = set(mcp_obj._tools.keys())
else:
    # Try listing via the tools dict
    for attr_name in dir(mcp_obj):
        obj = getattr(mcp_obj, attr_name, None)
        if callable(obj) and hasattr(obj, '_mcp_tool'):
            registered_tools.add(attr_name)

if registered_tools:
    print(f"  Found {len(registered_tools)} registered tools")
    for tool in sorted(expected_tools):
        check(f"  tool: {tool}", tool in registered_tools)
    extra = registered_tools - set(expected_tools)
    if extra:
        print(f"  {WARN} Extra tools (not in expected list): {extra}")
else:
    print(f"  {WARN} Could not introspect tools (FastMCP internals may vary)")
    print(f"  Checking tool functions exist instead...")
    for tool in expected_tools:
        check(f"  function: {tool}", hasattr(mcp_server, tool))


# ── Step 4: Prompts ────────────────────────────────────────────────

print("\n== Step 4: Registered Prompts ==")

expected_prompts = [
    # Core
    "status_check", "draft_email", "review_pr", "meeting_notes",
    "catch_me_up", "search_knowledge",
    # HR
    "interview_feedback", "onboarding_plan", "performance_review_prep", "policy_lookup",
    # Sales
    "deal_prep", "draft_proposal", "pipeline_review",
    # Product
    "draft_prd", "okr_update", "one_on_one_prep", "stakeholder_update",
    # Ops
    "create_sop", "compliance_check", "process_audit",
]

for prompt in expected_prompts:
    check(f"  prompt function: {prompt}", hasattr(mcp_server, prompt))


# ── Step 5: Resources ──────────────────────────────────────────────

print("\n== Step 5: Resources ==")

expected_resources = [
    "get_soul", "get_user_profile", "get_memory", "get_habits", "get_today_log"
]

for resource in expected_resources:
    check(f"  resource function: {resource}", hasattr(mcp_server, resource))


# ── Step 6: Skill Files ───────────────────────────────────────────

print("\n== Step 6: Skill Files ==")

skill_dirs = {
    "hr": ["interview-feedback", "onboarding-checklist", "performance-review", "policy-lookup", "pto-tracker"],
    "sales": ["deal-prep", "proposal-drafter", "follow-up", "competitive-analysis", "pipeline-review"],
    "product": ["prd-drafter", "okr-tracker", "one-on-one", "stakeholder-update", "feedback-synthesis"],
    "ops": ["sop-creator", "vendor-management", "compliance-checklist", "process-audit", "resource-allocation"],
}

for dept, skills in skill_dirs.items():
    for skill in skills:
        skill_path = PLUGIN_ROOT / "skills" / dept / skill / "SKILL.md"
        check(f"  skills/{dept}/{skill}/SKILL.md", skill_path.exists())


# ── Step 7: Vault Structure (for department files) ────────────────

print("\n== Step 7: Vault Department Directories ==")

dept_vault_dirs = [
    "hr/interviews", "hr/onboarding", "hr/reviews", "hr/policies", "hr/pto",
    "sales/briefs", "sales/proposals", "sales/follow-ups", "sales/competitors", "sales/pipeline",
    "product/prds", "product/okrs", "product/updates", "product/feedback",
    "ops/sops", "ops/vendors", "ops/compliance", "ops/audits", "ops/allocation",
]

if VAULT_DIR.exists():
    for d in dept_vault_dirs:
        check(f"  vault/{d}/", (VAULT_DIR / d).exists(), warn_only=True)
else:
    print(f"  {WARN} Vault doesn't exist yet — directories will be created on first use")
    warnings += 1


# ── Summary ────────────────────────────────────────────────────────

print(f"\n{'='*50}")
if errors == 0:
    print(f"{PASS} All checks passed! ({warnings} warnings)")
    print(f"\nThe MCP server is ready to run.")
    print(f"To start it: python3 {PLUGIN_ROOT}/mcp-server/server.py")
else:
    print(f"{FAIL} {errors} errors, {warnings} warnings")
    print(f"\nFix the errors above before running the MCP server.")

sys.exit(errors)
