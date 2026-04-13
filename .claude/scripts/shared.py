#!/usr/bin/env python3
"""
Command Guardrails — PreToolUse hook for security enforcement.

Runs before Bash, Write, and Edit tool calls. Enforces Vidit's security
boundaries via deterministic checks (no LLM cost).

Receives JSON on stdin: {tool_name, tool_input, session_id, cwd, ...}
Returns JSON on stdout with permissionDecision: allow/deny.

Exit codes:
    0 — Success (JSON parsed from stdout)
    2 — Blocking error (stderr fed back to Claude)

Security boundaries enforced:
    - Never send emails (block gmail send, allow drafts)
    - Never send Slack messages to channels (DM to Vidit allowed via bot only)
    - Never post to social media
    - Block destructive shell commands
    - Flag file modifications outside vault and .claude/
"""

import json
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


# ─── Destructive Command Patterns ────────────────────────────────

BLOCKED_COMMANDS = [
    # File destruction
    re.compile(r"\brm\s+-rf\s+/", re.I),
    re.compile(r"\brm\s+-rf\s+~", re.I),
    re.compile(r"\brm\s+-rf\s+\.\s", re.I),
    re.compile(r"\brm\s+-rf\s+\*", re.I),

    # Database destruction
    re.compile(r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b", re.I),
    re.compile(r"\bTRUNCATE\s+TABLE\b", re.I),
    re.compile(r"\bDELETE\s+FROM\s+\w+\s*;", re.I),  # DELETE without WHERE

    # System damage
    re.compile(r"\bmkfs\b", re.I),
    re.compile(r"\bdd\s+if=", re.I),
    re.compile(r"\bformat\s+[cC]:", re.I),
    re.compile(r":(){.*};:", re.I),  # Fork bomb

    # Credential exfiltration
    re.compile(r"\bcurl\b.*\b(GITHUB_TOKEN|ASANA_TOKEN|SLACK_BOT_TOKEN|AWS_SECRET|ANTHROPIC_API_KEY)", re.I),
    re.compile(r"\bwget\b.*\b(GITHUB_TOKEN|ASANA_TOKEN|SLACK_BOT_TOKEN|AWS_SECRET|ANTHROPIC_API_KEY)", re.I),

    # Email sending (should go through query.py draft, never send)
    re.compile(r"gmail.*send\b", re.I),
    re.compile(r"messages\.send", re.I),

    # Social media
    re.compile(r"\b(twitter|x\.com|facebook|instagram|linkedin|tiktok)\.com", re.I),
]

# Slack channel posting (block posts to channels, bot handles DM responses)
BLOCKED_SLACK_PATTERNS = [
    re.compile(r"chat\.postMessage", re.I),
    re.compile(r"chat_postMessage", re.I),
]

# Sensitive file patterns that should never be read/exposed
SENSITIVE_FILE_PATTERNS = [
    re.compile(r"\.env$"),
    re.compile(r"credentials\.json$"),
    re.compile(r"token\.json$"),
    re.compile(r"\.pem$"),
    re.compile(r"id_rsa"),
    re.compile(r"\.aws/credentials"),
]


def check_bash(command: str) -> dict:
    """Check a Bash command against security rules."""
    for pattern in BLOCKED_COMMANDS:
        if pattern.search(command):
            return deny(f"Blocked: command matches dangerous pattern '{pattern.pattern}'")

    for pattern in BLOCKED_SLACK_PATTERNS:
        if pattern.search(command):
            return deny("Blocked: Slack channel posting is not allowed. Use the bot for DM responses only.")

    # Check for cat/read of sensitive files
    for pattern in SENSITIVE_FILE_PATTERNS:
        if pattern.search(command) and any(cmd in command for cmd in ["cat ", "head ", "tail ", "less ", "more ", "echo "]):
            return deny(f"Blocked: cannot expose sensitive file contents via shell")

    return allow()


def check_write(file_path: str) -> dict:
    """Check if a file write is within allowed boundaries."""
    path = Path(file_path).resolve()
    project = Path(PROJECT_DIR).resolve()

    # Allowed write locations
    vault_dir = project / "Dynamous" / "Memory"
    claude_dir = project / ".claude"
    agent_dir = project / ".agent"

    allowed_prefixes = [str(vault_dir), str(claude_dir), str(agent_dir)]

    # Check if path is within allowed locations
    path_str = str(path)
    is_allowed = any(path_str.startswith(prefix) for prefix in allowed_prefixes)

    if not is_allowed:
        # Also allow files in the project root (like requirements.txt)
        if path_str.startswith(str(project)):
            # Soft allow with context — don't block but add context
            return allow(f"Note: writing outside vault/scripts to {file_path}")
        return deny(f"Blocked: file write outside project directory: {file_path}")

    # Block writing to sensitive files
    for pattern in SENSITIVE_FILE_PATTERNS:
        if pattern.search(file_path):
            return deny(f"Blocked: cannot write to sensitive file: {file_path}")

    return allow()


def check_edit(file_path: str) -> dict:
    """Check if a file edit is within allowed boundaries."""
    return check_write(file_path)


# ─── Decision Helpers ────────────────────────────────────────────

def allow(context: str = "") -> dict:
    """Return an allow decision."""
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }
    if context:
        result["hookSpecificOutput"]["additionalContext"] = context
    return result


def deny(reason: str) -> dict:
    """Return a deny decision."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "additionalContext": reason,
        }
    }


# ─── Main ────────────────────────────────────────────────────────

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        # Can't parse input — allow by default (non-blocking)
        json.dump(allow(), sys.stdout)
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        decision = check_bash(command)

    elif tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        decision = check_write(file_path)

    else:
        decision = allow()

    json.dump(decision, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
