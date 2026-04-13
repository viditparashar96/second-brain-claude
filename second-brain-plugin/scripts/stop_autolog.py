#!/usr/bin/env python3
"""Stop Hook — Auto-detect important items from the last assistant message and log to daily vault."""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DAILY_DIR, LOG_DIR


def log_error(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "hooks.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] stop-autolog: {msg}\n")
    except Exception:
        pass


def extract_important(text):
    """Extract important items from assistant's last message using heuristics."""
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()

        is_important = (
            "decided" in lower or "decision:" in lower or
            "action item" in lower or "todo:" in lower or
            "will " in lower and ("create" in lower or "implement" in lower or "build" in lower or "fix" in lower) or
            "created file" in lower or "created draft" in lower or
            "draft created" in lower or
            "saved to" in lower or "wrote" in lower and "lines to" in lower or
            re.match(r"^#{1,3}\s", stripped) and len(stripped) > 15
        )

        if is_important:
            clean = stripped.lstrip("#-* ").strip()
            if len(clean) > 15 and clean not in items:
                items.append(clean[:200])

    return items[:5]  # Max 5 items per turn


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    last_message = input_data.get("last_assistant_message", "")
    if not last_message:
        # Try to extract from content blocks
        content = input_data.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    last_message += block.get("text", "") + "\n"

    if not last_message or len(last_message) < 50:
        sys.exit(0)

    items = extract_important(last_message)
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
