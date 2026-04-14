#!/usr/bin/env python3
"""SessionStart Hook — Inject memory context into every new conversation."""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, LOG_DIR


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


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    parts = [
        read_file(VAULT_DIR / "SOUL.md", "SOUL"),
        read_file(VAULT_DIR / "USER.md", "USER"),
        read_file(VAULT_DIR / "MEMORY.md", "MEMORY"),
        get_recent_daily_logs(VAULT_DIR / "daily", count=3),
        read_file(VAULT_DIR / "HABITS.md", "HABITS"),
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
