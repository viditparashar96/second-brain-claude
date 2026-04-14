#!/usr/bin/env python3
"""SessionEnd Hook — Save conversation context when the session ends."""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DAILY_DIR, LOG_DIR

FLUSH_MARKER = "[auto-saved on session end]"


def log_error(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "hooks.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] session-end: {msg}\n")
    except Exception:
        pass


def get_last_flush_time(log_path):
    if not log_path.exists():
        return None
    try:
        content = log_path.read_text()
        matches = re.findall(r"\*\*(\d{2}:\d{2})\*\* — \[auto-saved", content)
        if matches:
            today = datetime.now().date()
            return datetime.combine(today, datetime.strptime(matches[-1], "%H:%M").time())
    except Exception as e:
        log_error(f"Error checking last flush: {e}")
    return None


def extract_assistant_messages(transcript_path, after=None):
    messages = []
    try:
        with open(transcript_path, "r") as f:
            lines = f.readlines()
        start_line = 0
        if after:
            minutes_since = (datetime.now() - after).total_seconds() / 60
            if minutes_since < 5:
                start_line = max(0, len(lines) - (len(lines) // 4))
        for line in lines[start_line:]:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("role") == "assistant":
                content = entry.get("content", [])
                if isinstance(content, str):
                    messages.append(content)
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text" and block.get("text"):
                            messages.append(block["text"])
    except Exception as e:
        log_error(f"Error reading transcript: {e}")
    return messages


def extract_key_points(messages):
    key_points = []
    for msg in messages:
        for line in msg.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            lower = stripped.lower()
            is_important = (
                stripped.startswith("- [") or "decision:" in lower or
                "action item:" in lower or "todo:" in lower or
                "important:" in lower or "created file" in lower or
                "updated file" in lower or re.match(r"^#{1,3}\s", stripped)
            )
            if is_important:
                clean = stripped.lstrip("#").strip()
                if len(clean) > 10 and clean not in key_points:
                    key_points.append(clean)
    return key_points


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    transcript_path = input_data.get("transcript_path", "")
    if not transcript_path:
        sys.exit(0)

    log_path = DAILY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    last_flush = get_last_flush_time(log_path)
    messages = extract_assistant_messages(transcript_path, after=last_flush)

    if not messages:
        sys.exit(0)

    key_points = extract_key_points(messages)
    if not key_points:
        sys.exit(0)

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%H:%M")
    entry_lines = [f"- **{now}** — {FLUSH_MARKER}"]
    for point in key_points[:20]:
        entry_lines.append(f"  - {point}")
    entry = "\n".join(entry_lines) + "\n"

    try:
        if log_path.exists():
            content = log_path.read_text()
            if not content.endswith("\n"):
                entry = "\n" + entry
        else:
            entry = f"# Daily Log — {datetime.now().strftime('%Y-%m-%d')}\n\n## Log\n\n" + entry
        with open(log_path, "a") as f:
            f.write(entry)
    except Exception as e:
        log_error(f"Failed to write daily log: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
