#!/usr/bin/env python3
"""PreToolUse Guardrails Hook — Security enforcement for Bash/Write/Edit."""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, SECOND_BRAIN_HOME

BLOCKED_COMMANDS = [
    re.compile(r"\brm\s+-rf\s+/", re.I),
    re.compile(r"\brm\s+-rf\s+~", re.I),
    re.compile(r"\brm\s+-rf\s+\.\s", re.I),
    re.compile(r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b", re.I),
    re.compile(r"\bTRUNCATE\s+TABLE\b", re.I),
    re.compile(r"\bmkfs\b", re.I),
    re.compile(r"\bdd\s+if=", re.I),
    re.compile(r"\bcurl\b.*\b(GITHUB_TOKEN|ASANA_TOKEN|SLACK_BOT_TOKEN|AWS_SECRET|ANTHROPIC_API_KEY)", re.I),
    re.compile(r"gmail.*send\b", re.I),
    re.compile(r"messages\.send", re.I),
    re.compile(r"\b(twitter|x\.com|facebook|instagram|linkedin|tiktok)\.com", re.I),
]

BLOCKED_SLACK = [
    re.compile(r"chat\.postMessage", re.I),
    re.compile(r"chat_postMessage", re.I),
]

SENSITIVE_FILES = [
    re.compile(r"\.env$"),
    re.compile(r"credentials\.json$"),
    re.compile(r"token\.json$"),
    re.compile(r"\.pem$"),
    re.compile(r"id_rsa"),
]


def allow(context=""):
    r = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
    if context:
        r["hookSpecificOutput"]["additionalContext"] = context
    return r


def deny(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "additionalContext": reason}}


def check_bash(command):
    for p in BLOCKED_COMMANDS:
        if p.search(command):
            return deny(f"Blocked: dangerous pattern '{p.pattern}'")
    for p in BLOCKED_SLACK:
        if p.search(command):
            return deny("Blocked: Slack channel posting not allowed")
    for p in SENSITIVE_FILES:
        if p.search(command) and any(cmd in command for cmd in ["cat ", "head ", "tail ", "less "]):
            return deny("Blocked: cannot expose sensitive file contents")
    return allow()


def check_write(file_path):
    path = Path(file_path).resolve()
    vault = VAULT_DIR.resolve()
    sb_home = SECOND_BRAIN_HOME.resolve()

    if str(path).startswith(str(vault)) or str(path).startswith(str(sb_home)):
        for p in SENSITIVE_FILES:
            if p.search(file_path):
                return deny(f"Blocked: cannot write to sensitive file: {file_path}")
        return allow()

    return allow(f"Note: writing outside Second Brain vault to {file_path}")


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        json.dump(allow(), sys.stdout)
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "Bash":
        decision = check_bash(tool_input.get("command", ""))
    elif tool_name in ("Write", "Edit"):
        decision = check_write(tool_input.get("file_path", ""))
    else:
        decision = allow()

    json.dump(decision, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
