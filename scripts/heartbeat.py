#!/usr/bin/env python3
"""Heartbeat — Proactive monitoring. Gathers data from integrations, diffs, notifies."""

import argparse
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, DAILY_DIR, STATE_DIR, LOG_DIR, SECOND_BRAIN_HOME, load_config, get_enabled_integrations

IST = timezone(timedelta(hours=5, minutes=30))
STATE_FILE = STATE_DIR / "heartbeat-state.json"


def log(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "heartbeat.log", "a") as f:
            f.write(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def is_active_hours():
    return 9 <= datetime.now(IST).hour < 21


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def _run_query(*args):
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", str(Path(__file__).resolve().parent.parent))
    query_py = str(Path(plugin_root) / "scripts" / "integrations" / "query.py")
    venv_python = str(SECOND_BRAIN_HOME / ".venv" / "bin" / "python3")
    python = venv_python if Path(venv_python).exists() else sys.executable
    try:
        result = subprocess.run(
            [python, query_py, *args],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "SECOND_BRAIN_HOME": str(SECOND_BRAIN_HOME)},
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def gather_gmail():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "integrations"))
        from gmail.client import list_emails
        unread = list_emails(limit=50, unread_only=True)
        return {"unread_count": len(unread), "unread_subjects": [
            {"id": e.id, "from": e.sender, "subject": e.subject} for e in unread[:10]
        ]}
    except Exception as e:
        log(f"Gmail: {e}")
        return {"error": str(e)}


def gather_asana():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "integrations"))
        from asana_int.client import get_overdue_tasks, get_upcoming_tasks
        overdue = get_overdue_tasks()
        upcoming = get_upcoming_tasks(days=7)
        return {
            "overdue_count": len(overdue),
            "overdue_tasks": [{"gid": t.gid, "name": t.name, "due_on": t.due_on} for t in overdue[:10]],
            "upcoming_count": len(upcoming),
            "upcoming_tasks": [{"gid": t.gid, "name": t.name, "due_on": t.due_on} for t in upcoming[:10]],
        }
    except Exception as e:
        log(f"Asana: {e}")
        return {"error": str(e)}


def gather_github():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "integrations"))
        from gh.client import get_rate_limit
        return {"rate_limit_remaining": get_rate_limit()["core_remaining"]}
    except Exception as e:
        log(f"GitHub: {e}")
        return {"error": str(e)}


def gather_gcal():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "integrations"))
        from gcal.client import get_upcoming
        upcoming = get_upcoming(minutes=30)
        return {
            "upcoming_count": len(upcoming),
            "upcoming_events": [
                {"summary": e.summary, "start": e.start.isoformat(), "attendees": e.attendees[:5]}
                for e in upcoming
            ],
        }
    except Exception as e:
        log(f"Calendar: {e}")
        return {"error": str(e)}


def gather_meeting_followups():
    try:
        from meeting_followups import get_overdue_items, get_due_today
        overdue = get_overdue_items()
        due_today = get_due_today()
        return {
            "overdue_count": len(overdue),
            "overdue_items": overdue[:5],
            "due_today_count": len(due_today),
            "due_today_items": due_today[:5],
        }
    except Exception as e:
        log(f"Meeting followups: {e}")
        return {"error": str(e)}


def gather_all():
    enabled = get_enabled_integrations()
    snapshot = {"timestamp": datetime.now(IST).isoformat()}
    if "gmail" in enabled:
        snapshot["gmail"] = gather_gmail()
    if "gcal" in enabled:
        snapshot["gcal"] = gather_gcal()
    if "asana" in enabled:
        snapshot["asana"] = gather_asana()
    if "github" in enabled:
        snapshot["github"] = gather_github()
    snapshot["meeting_followups"] = gather_meeting_followups()
    return snapshot


def diff_snapshots(old, new):
    changes = {"urgent": [], "info": []}

    new_gmail = new.get("gmail", {})
    if "error" not in new_gmail:
        old_unread = old.get("gmail", {}).get("unread_count", 0)
        new_unread = new_gmail.get("unread_count", 0)
        if new_unread > old_unread:
            changes["info"].append(f"{new_unread - old_unread} new unread email(s)")

    new_asana = new.get("asana", {})
    if "error" not in new_asana and new_asana.get("overdue_count", 0) > 0:
        changes["urgent"].append(f"{new_asana['overdue_count']} overdue Asana task(s)")
        for t in new_asana.get("overdue_tasks", [])[:3]:
            changes["urgent"].append(f"  - {t['name']} (due {t['due_on']})")

    # Upcoming meetings
    new_gcal = new.get("gcal", {})
    if "error" not in new_gcal and new_gcal.get("upcoming_count", 0) > 0:
        for e in new_gcal.get("upcoming_events", [])[:2]:
            changes["urgent"].append(f"Meeting soon: {e['summary']} at {e['start']}")

    # Meeting follow-up action items
    followups = new.get("meeting_followups", {})
    if "error" not in followups:
        overdue_count = followups.get("overdue_count", 0)
        if overdue_count > 0:
            changes["urgent"].append(f"{overdue_count} overdue meeting action item(s)")
            for item in followups.get("overdue_items", [])[:3]:
                owner = f" [{item['owner']}]" if item.get("owner") else ""
                changes["urgent"].append(f"  - {item['action']}{owner} (due {item['due_date']})")
        due_today_count = followups.get("due_today_count", 0)
        if due_today_count > 0:
            changes["info"].append(f"{due_today_count} meeting action item(s) due today")

    return changes


def check_habits():
    habits_path = VAULT_DIR / "HABITS.md"
    if not habits_path.exists() or datetime.now(IST).hour < 17:
        return []
    try:
        content = habits_path.read_text()
        unchecked = []
        for line in content.split("\n"):
            if line.strip().startswith("- [ ] **"):
                pillar = line.split("**")[1] if "**" in line else line.strip()
                unchecked.append(pillar)
        if unchecked:
            return [f"Late-day nudge: {len(unchecked)} unchecked pillar(s): {', '.join(unchecked)}"]
    except Exception:
        pass
    return []


def expire_old_drafts():
    active = VAULT_DIR / "drafts" / "active"
    expired = VAULT_DIR / "drafts" / "expired"
    if not active.exists():
        return
    expired.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now() - timedelta(hours=24)
    for f in active.glob("*.md"):
        try:
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                f.rename(expired / f.name)
        except Exception:
            pass


def notify(items):
    if not items:
        return
    try:
        msg = items[0] if len(items) == 1 else f"{len(items)} items need attention"
        subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "Second Brain"'],
                       capture_output=True, timeout=5)
    except Exception:
        pass


def append_to_daily(summary):
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(IST).strftime("%Y-%m-%d")
    log_path = DAILY_DIR / f"{today}.md"
    now = datetime.now(IST).strftime("%H:%M")
    entry = f"- **{now}** — [heartbeat] {summary}\n"
    try:
        if log_path.exists():
            content = log_path.read_text()
            if not content.endswith("\n"):
                entry = "\n" + entry
        else:
            entry = f"# Daily Log — {today}\n\n## Log\n\n" + entry
        with open(log_path, "a") as f:
            f.write(entry)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.force and not is_active_hours():
        return

    log("Heartbeat started")
    snapshot = gather_all()
    old_state = load_state()
    changes = diff_snapshots(old_state, snapshot)
    changes["info"].extend(check_habits())
    expire_old_drafts()

    all_items = changes["urgent"] + changes["info"]

    if args.dry_run:
        print(f"Timestamp: {snapshot['timestamp']}")
        print(f"Urgent: {changes['urgent'] or ['None']}")
        print(f"Info: {changes['info'] or ['None']}")
        return

    if changes["urgent"]:
        notify(changes["urgent"])

    if all_items:
        summary = " | ".join(
            ([f"URGENT: {'; '.join(changes['urgent'][:3])}"] if changes["urgent"] else []) +
            ([f"Info: {'; '.join(changes['info'][:3])}"] if changes["info"] else [])
        )
        append_to_daily(summary)

    save_state(snapshot)
    log(f"Done. {len(all_items)} changes, {len(changes['urgent'])} urgent")
    print(f"Heartbeat complete. {len(all_items)} changes ({len(changes['urgent'])} urgent).")


if __name__ == "__main__":
    main()
