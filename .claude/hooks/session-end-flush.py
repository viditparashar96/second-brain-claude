#!/usr/bin/env python3
"""
SessionEnd Hook — Save conversation context when the session ends.

Similar to PreCompact, but runs at session termination. Avoids duplicating
content that PreCompact already saved by checking the last flush marker
timestamp in today's daily log.

Receives JSON on stdin: {session_id, transcript_path, cwd, ...}
Always exits 0. Errors logged to file.
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

FLUSH_MARKER = "[auto-saved on session end]"
COMPACT_MARKER = "[auto-saved before compaction]"


def log_error(msg: str):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] session-end: {msg}\n")
    except Exception:
        pass


def get_today_log_path() -> Path:
    return DAILY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"


def get_last_flush_time(log_path: Path) -> datetime | None:
    """Check when the last PreCompact flush happened today."""
    if not log_path.exists():
        return None

    try:
        content = log_path.read_text(encoding="utf-8")
        # Find all auto-saved markers with timestamps
        pattern = r"\*\*(\d{2}:\d{2})\*\* — \[auto-saved"
        matches = re.findall(pattern, content)
        if matches:
            last_time_str = matches[-1]
            today = datetime.now().date()
            return datetime.combine(
                today,
                datetime.strptime(last_time_str, "%H:%M").time()
            )
    except Exception as e:
        log_error(f"Error checking last flush time: {e}")

    return None


def extract_assistant_messages(transcript_path: str, after: datetime | None = None) -> list[str]:
    """Read JSONL transcript and extract assistant text messages.

    If `after` is set, only include messages from transcript entries
    that appear after the last flush (by position in file, since
    JSONL entries don't have timestamps — we use line position as proxy).
    """
    messages = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # If we had a recent flush, skip roughly the first portion of the transcript.
        # This is a heuristic — the daily reflection (Phase 6) handles dedup properly.
        start_line = 0
        if after:
            minutes_since_flush = (datetime.now() - after).total_seconds() / 60
            if minutes_since_flush < 5:
                # Very recent flush — skip most of the transcript
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
    """Extract likely important points from assistant messages."""
    key_points = []

    for msg in messages:
        lines = msg.split("\n")
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            lower = stripped.lower()
            is_important = (
                stripped.startswith("- [") or
                "decision:" in lower or
                "action item:" in lower or
                "todo:" in lower or
                "important:" in lower or
                "note:" in lower or
                "created file" in lower or
                "updated file" in lower or
                re.match(r"^#{1,3}\s", stripped)
            )

            if is_important:
                clean = stripped.lstrip("#").strip()
                if len(clean) > 10 and clean not in key_points:
                    key_points.append(clean)

    return key_points


def append_to_daily_log(key_points: list[str]):
    """Append extracted key points to today's daily log."""
    if not key_points:
        return

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    log_path = get_today_log_path()

    now = datetime.now().strftime("%H:%M")
    entry_lines = [
        f"- **{now}** — {FLUSH_MARKER}",
    ]
    for point in key_points[:20]:
        entry_lines.append(f"  - {point}")

    entry = "\n".join(entry_lines) + "\n"

    try:
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8")
            if not content.endswith("\n"):
                entry = "\n" + entry
        else:
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

    if not transcript_path:
        log_error("No transcript_path in stdin data")
        sys.exit(0)

    # Check if PreCompact already flushed recently
    log_path = get_today_log_path()
    last_flush = get_last_flush_time(log_path)

    messages = extract_assistant_messages(transcript_path, after=last_flush)
    if messages:
        key_points = extract_key_points(messages)
        append_to_daily_log(key_points)

    sys.exit(0)


if __name__ == "__main__":
    main()
