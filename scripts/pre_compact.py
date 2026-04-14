#!/usr/bin/env python3
"""PreCompact Hook — Save conversation context before auto-compaction."""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DAILY_DIR, LOG_DIR, get_memory_level

FLUSH_MARKER = "[auto-saved before compaction]"


def log_error(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "hooks.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] pre-compact: {msg}\n")
    except Exception:
        pass


def extract_assistant_messages(transcript_path):
    messages = []
    try:
        with open(transcript_path, "r") as f:
            for line in f:
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
                            if isinstance(block, dict) and block.get("type") == "text":
                                text = block.get("text", "")
                                if text:
                                    messages.append(text)
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
    if get_memory_level() == "off":
        sys.exit(0)

    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    transcript_path = input_data.get("transcript_path", "")
    context_size = input_data.get("context_size_before", 0)

    if not transcript_path:
        sys.exit(0)

    messages = extract_assistant_messages(transcript_path)
    if not messages:
        sys.exit(0)

    key_points = extract_key_points(messages)
    if not key_points:
        sys.exit(0)

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    log_path = DAILY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    now = datetime.now().strftime("%H:%M")

    entry_lines = [f"- **{now}** — {FLUSH_MARKER} (context: {context_size:,} tokens)"]
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
