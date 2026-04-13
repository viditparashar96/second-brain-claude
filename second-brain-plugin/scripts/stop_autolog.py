#!/usr/bin/env python3
"""
Stop Hook — Intelligently extract important items from conversations and log to daily vault.

Uses Claude CLI (free with Claude Max) for intelligent extraction.
Falls back to heuristics if CLI is not available.
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DAILY_DIR, LOG_DIR

CLAUDE_CLI = shutil.which("claude")


def log_error(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "hooks.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] stop-autolog: {msg}\n")
    except Exception:
        pass


def extract_with_cli(text):
    """Use Claude CLI to intelligently extract important items."""
    if not CLAUDE_CLI:
        return None

    prompt = f"""Extract ONLY genuinely important items from this conversation turn. Return a JSON array of short strings (1 line each). Include:
- Decisions made (technical choices, architecture, tool selection)
- Action items (who will do what, deadlines)
- New project info (project names, tech stacks, goals)
- Key facts learned (client info, team context, constraints)
- Files created or major changes

Return [] if nothing noteworthy. ONLY return the JSON array, nothing else.

Conversation:
{text[:3000]}"""

    try:
        result = subprocess.run(
            [CLAUDE_CLI, "--print", "-p", prompt],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return None

        output = result.stdout.strip()
        # Extract JSON array from response
        match = re.search(r'\[.*\]', output, re.DOTALL)
        if match:
            items = json.loads(match.group())
            if isinstance(items, list):
                return [str(item)[:200] for item in items if item][:5]
    except Exception as e:
        log_error(f"CLI extraction failed: {e}")

    return None


def extract_heuristic(text):
    """Fallback: extract using keyword matching."""
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()

        is_important = (
            "decided" in lower or "decision:" in lower or
            "action item" in lower or "todo:" in lower or
            "will " in lower and ("create" in lower or "implement" in lower or "build" in lower) or
            "created file" in lower or "created draft" in lower or
            "saved to" in lower or
            re.match(r"^#{1,3}\s", stripped) and len(stripped) > 15
        )

        if is_important:
            clean = stripped.lstrip("#-* ").strip()
            if len(clean) > 15 and clean not in items:
                items.append(clean[:200])

    return items[:5]


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    last_message = input_data.get("last_assistant_message", "")
    if not last_message:
        content = input_data.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    last_message += block.get("text", "") + "\n"

    if not last_message or len(last_message) < 50:
        sys.exit(0)

    # Try CLI first (intelligent), fall back to heuristics
    items = extract_with_cli(last_message)
    if items is None:
        items = extract_heuristic(last_message)

    if not items:
        sys.exit(0)

    # Write to daily log
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = DAILY_DIR / f"{today}.md"
    now = datetime.now().strftime("%H:%M")

    entry_lines = [f"- **{now}** — [auto] {items[0]}"]
    for item in items[1:]:
        entry_lines.append(f"  - {item}")
    entry = "\n".join(entry_lines) + "\n"

    try:
        if log_path.exists():
            content = log_path.read_text()
            if not content.endswith("\n"):
                entry = "\n" + entry
        else:
            entry = f"# Daily Log — {today}\n\n## Log\n\n" + entry

        with open(log_path, "a") as f:
            f.write(entry)
    except Exception as e:
        log_error(f"Failed to write: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
