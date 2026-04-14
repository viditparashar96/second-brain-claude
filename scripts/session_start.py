#!/usr/bin/env python3
"""SessionStart Hook — Inject memory context into every new conversation."""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, LOG_DIR, get_memory_level, get_enabled_integrations


def log_error(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "hooks.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] session-start: {msg}\n")
    except Exception:
        pass


def read_file(path, label):
    try:
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                return f"## {label}\n\n{content}"
    except Exception as e:
        log_error(f"Failed to read {path}: {e}")
    return ""


def get_recent_daily_logs(daily_dir, count=3):
    if not daily_dir.exists():
        return ""
    log_files = sorted(daily_dir.glob("*.md"), reverse=True)[:count]
    sections = []
    for lf in log_files:
        try:
            content = lf.read_text(encoding="utf-8").strip()
            if content:
                sections.append(content)
        except Exception as e:
            log_error(f"Failed to read {lf}: {e}")
    if sections:
        return "## Recent Daily Logs\n\n" + "\n\n---\n\n".join(sections)
    return ""


def get_calendar_context():
    """Fetch today's calendar events if gcal is enabled."""
    try:
        if "gcal" not in get_enabled_integrations():
            return ""
        sys.path.insert(0, str(Path(__file__).resolve().parent / "integrations"))
        from gcal.client import list_events, format_event_list
        events = list_events(days=1)
        if not events:
            return ""
        formatted = format_event_list(events)
        return f"## Today's Calendar\n\n{formatted}"
    except Exception as e:
        log_error(f"Calendar context failed: {e}")
        return ""


def get_meeting_followups():
    """Fetch overdue and due-today meeting action items."""
    try:
        from meeting_followups import get_overdue_items, get_due_today, format_items_text
        parts = []
        overdue = get_overdue_items()
        if overdue:
            parts.append(format_items_text(overdue, "Overdue Meeting Action Items"))
        due_today = get_due_today()
        if due_today:
            parts.append(format_items_text(due_today, "Meeting Action Items Due Today"))
        if parts:
            return "## Meeting Follow-ups\n\n" + "\n\n".join(parts)
    except Exception as e:
        log_error(f"Meeting followups failed: {e}")
    return ""


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    # Check memory level — if "off", skip memory injection
    if get_memory_level() == "off":
        sys.exit(0)

    parts = [
        read_file(VAULT_DIR / "SOUL.md", "SOUL"),
        read_file(VAULT_DIR / "USER.md", "USER"),
        read_file(VAULT_DIR / "MEMORY.md", "MEMORY"),
        get_recent_daily_logs(VAULT_DIR / "daily", count=3),
        read_file(VAULT_DIR / "HABITS.md", "HABITS"),
        get_calendar_context(),
        get_meeting_followups(),
    ]

    context = "\n\n---\n\n".join(p for p in parts if p)
    if not context:
        context = "Second Brain vault not found. Run /second-brain:setup first."

    if len(context) > 9500:
        context = context[:9500] + "\n\n... (truncated)"

    print(context)
    sys.exit(0)


if __name__ == "__main__":
    main()
