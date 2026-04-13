#!/usr/bin/env python3
"""
PreCompact Hook — Save conversation context before auto-compaction.

Reads the JSONL transcript, extracts key decisions, facts, and action items,
and appends them to today's daily log with timestamps.

Always exits 0 — we never want to block compaction. Errors logged to file.

Receives JSON on stdin: {session_id, transcript_path, cwd, trigger, context_size_before, ...}
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
VAULT_DIR = Path(PROJECT_DIR) / "Dynamous" / "Memory"
DAILY_DIR = VAULT_DIR / "daily"
LOG_FILE = Path(PROJECT_DIR) / ".claude" / "data" / "logs" / "hooks.log"

# Markers for deduplication — we write this tag so SessionEnd can detect what was already flushed
FLUSH_MARKER = "[auto-saved before compaction]"


def log_error(msg: str):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] pre-compact: {msg}\n")
    except Exception:
        pass


def get_today_log_path() -> Path:
    return DAILY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"


def extract_assistant_messages(transcript_path: str) -> list[str]:
    """Read JSONL transcript and extract assistant text messages."""
    messages = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Extract text from assistant messages
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
    except FileNotFoundError:
        log_error(f"Transcript not found: {transcript_path}")
    except Exception as e:
        log_error(f"Error reading transcript: {e}")

    return messages


def extract_key_points(messages: list[str]) -> list[str]:
    """Extract likely important points from assistant messages.

    Uses heuristics to find decisions, action items, and key facts.
    This is a lightweight extraction — the daily reflection (Phase 6)
    will do a more thorough LLM-based review later.
    """
    key_points = []

    for msg in messages:
        lines = msg.split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Action items and decisions (common patterns)
            lower = stripped.lower()
            is_important = (
                stripped.startswith("- [") or  # Checklist items
                "decision:" in lower or
                "action item:" in lower or
                "todo:" in lower or
                "important:" in lower or
                "note:" in lower or
                "created file" in lower or
                "updated file" in lower or
                re.match(r"^#{1,3}\s", stripped)  # Headers indicate structure
            )

            if is_important:
                # Clean up the line
                clean = stripped.lstrip("#").strip()
                if len(clean) > 10 and clean not in key_points:
                    key_points.append(clean)

    return key_points


def append_to_daily_log(key_points: list[str], context_size: int):
    """Append extracted key points to today's daily log."""
    if not key_points:
        return

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    log_path = get_today_log_path()

    now = datetime.now().strftime("%H:%M")
    entry_lines = [
        f"- **{now}** — {FLUSH_MARKER} (context: {context_size:,} tokens)",
    ]
    for point in key_points[:20]:  # Cap at 20 items to avoid bloat
        entry_lines.append(f"  - {point}")

    entry = "\n".join(entry_lines) + "\n"

    try:
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8")
            if not content.endswith("\n"):
                entry = "\n" + entry
        else:
            # Create new daily log with header
            header = f"# Daily Log — {datetime.now().strftime('%Y-%m-%d')}\n\n## Log\n\n"
            entry = header + entry

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    except Exception as e:
        log_error(f"Failed to write daily log: {e}")


def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    transcript_path = input_data.get("transcript_path", "")
    context_size = input_data.get("context_size_before", 0)

    if not transcript_path:
        log_error("No transcript_path in stdin data")
        sys.exit(0)

    messages = extract_assistant_messages(transcript_path)
    if messages:
        key_points = extract_key_points(messages)
        append_to_daily_log(key_points, context_size)

    # Always exit 0 — never block compaction
    sys.exit(0)


if __name__ == "__main__":
    main()
