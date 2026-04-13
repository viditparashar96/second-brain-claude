#!/usr/bin/env python3
"""
SessionStart Hook — Inject memory context into every new conversation.

Reads SOUL.md + USER.md + MEMORY.md + last 3 daily logs and outputs
the combined context as a string on stdout. Claude Code injects this
into the conversation automatically.

Receives JSON on stdin: {session_id, transcript_path, cwd, source, ...}
Output: context string on stdout, exit 0.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Resolve vault path relative to project dir
PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
VAULT_DIR = Path(PROJECT_DIR) / "Dynamous" / "Memory"
LOG_FILE = Path(PROJECT_DIR) / ".claude" / "data" / "logs" / "hooks.log"


def log_error(msg: str):
    """Log errors to file, never stderr (avoids corrupting JSON parsing)."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] session-start: {msg}\n")
    except Exception:
        pass


def read_file(path: Path, label: str) -> str:
    """Read a vault file, return its content with a header label."""
    try:
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                return f"## {label}\n\n{content}"
    except Exception as e:
        log_error(f"Failed to read {path}: {e}")
    return ""


def get_recent_daily_logs(daily_dir: Path, count: int = 3) -> str:
    """Read the most recent N daily log files."""
    if not daily_dir.exists():
        return ""

    log_files = sorted(daily_dir.glob("*.md"), reverse=True)[:count]
    if not log_files:
        return ""

    sections = []
    for log_file in log_files:
        try:
            content = log_file.read_text(encoding="utf-8").strip()
            if content:
                sections.append(content)
        except Exception as e:
            log_error(f"Failed to read daily log {log_file}: {e}")

    if sections:
        return "## Recent Daily Logs\n\n" + "\n\n---\n\n".join(sections)
    return ""


def main():
    # Read stdin (hook input JSON) — consume it even if we don't need all fields
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    parts = []

    # Core identity files
    parts.append(read_file(VAULT_DIR / "SOUL.md", "SOUL"))
    parts.append(read_file(VAULT_DIR / "USER.md", "USER"))
    parts.append(read_file(VAULT_DIR / "MEMORY.md", "MEMORY"))

    # Recent daily logs for short-term context
    parts.append(get_recent_daily_logs(VAULT_DIR / "daily", count=3))

    # Habits for today's awareness
    parts.append(read_file(VAULT_DIR / "HABITS.md", "HABITS"))

    # Filter empty parts and combine
    context = "\n\n---\n\n".join(p for p in parts if p)

    if not context:
        context = "Memory vault not found or empty. Run Phase 1 setup first."

    # Truncate to stay within the 10,000 char hook output cap
    if len(context) > 9500:
        context = context[:9500] + "\n\n... (truncated — vault context exceeds hook output limit)"

    # Output context as plain text on stdout
    print(context)
    sys.exit(0)


if __name__ == "__main__":
    main()
