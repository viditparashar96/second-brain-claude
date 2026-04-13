#!/usr/bin/env python3
"""
Heartbeat — Proactive monitoring orchestrator.

Runs every 30 minutes during active hours (9:00-21:00 IST).
Gathers data from all integrations, diffs against last state,
optionally reasons with Claude, and notifies about urgent items.

Usage:
    python heartbeat.py [--force] [--no-llm] [--dry-run]

Options:
    --force     Run even outside active hours
    --no-llm    Skip Claude reasoning (just gather + diff + notify)
    --dry-run   Print what would happen without writing state or notifying
"""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add scripts dir to path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR / "integrations"))

from heartbeat_notify import notify, notify_urgent

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(SCRIPTS_DIR.parent.parent)
)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

VAULT_DIR = Path(PROJECT_DIR) / "Dynamous" / "Memory"
STATE_FILE = Path(PROJECT_DIR) / ".claude" / "data" / "state" / "heartbeat-state.json"
LOG_FILE = Path(PROJECT_DIR) / ".claude" / "data" / "logs" / "heartbeat.log"
DAILY_DIR = VAULT_DIR / "daily"

# IST = UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


def log(msg: str):
    """Append to heartbeat log file."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass


def is_active_hours() -> bool:
    """Check if current IST time is within 9:00-21:00."""
    now = datetime.now(IST)
    return 9 <= now.hour < 21


def load_state() -> dict:
    """Load last heartbeat state from disk."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict):
    """Save heartbeat state to disk."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


# ─── Data Gathering ──────────────────────────────────────────────

def gather_gmail() -> dict:
    """Gather Gmail data: unread count and emails needing replies."""
    try:
        from gmail.client import list_emails
        unread = list_emails(limit=50, unread_only=True)
        return {
            "unread_count": len(unread),
            "unread_subjects": [
                {"id": e.id, "from": e.sender, "subject": e.subject}
                for e in unread[:10]
            ],
        }
    except Exception as e:
        log(f"Gmail gather failed: {e}")
        return {"error": str(e)}


def gather_github() -> dict:
    """Gather GitHub data: open PRs and recent issues."""
    try:
        from gh.client import list_prs, list_issues, get_rate_limit

        # Get repos from USER.md or env
        # For now, use a simple approach — gather from all accessible repos
        rl = get_rate_limit()

        return {
            "rate_limit_remaining": rl["core_remaining"],
        }
    except Exception as e:
        log(f"GitHub gather failed: {e}")
        return {"error": str(e)}


def gather_asana() -> dict:
    """Gather Asana data: overdue and upcoming tasks."""
    try:
        from asana_int.client import get_overdue_tasks, get_upcoming_tasks

        overdue = get_overdue_tasks()
        upcoming = get_upcoming_tasks(days=7)

        return {
            "overdue_count": len(overdue),
            "overdue_tasks": [
                {"gid": t.gid, "name": t.name, "due_on": t.due_on, "assignee": t.assignee}
                for t in overdue[:10]
            ],
            "upcoming_count": len(upcoming),
            "upcoming_tasks": [
                {"gid": t.gid, "name": t.name, "due_on": t.due_on, "assignee": t.assignee}
                for t in upcoming[:10]
            ],
        }
    except Exception as e:
        log(f"Asana gather failed: {e}")
        return {"error": str(e)}


def gather_all() -> dict:
    """Gather data from all integrations."""
    return {
        "timestamp": datetime.now(IST).isoformat(),
        "gmail": gather_gmail(),
        "github": gather_github(),
        "asana": gather_asana(),
    }


# ─── Snapshot Diffing ────────────────────────────────────────────

def diff_snapshots(old: dict, new: dict) -> dict:
    """Compare two snapshots and return what changed."""
    changes = {"urgent": [], "info": []}

    # Gmail changes
    old_gmail = old.get("gmail", {})
    new_gmail = new.get("gmail", {})
    if "error" not in new_gmail:
        old_unread = old_gmail.get("unread_count", 0)
        new_unread = new_gmail.get("unread_count", 0)
        if new_unread > old_unread:
            diff = new_unread - old_unread
            changes["info"].append(f"{diff} new unread email(s)")
            # Check for important senders in new unread
            old_ids = {e["id"] for e in old_gmail.get("unread_subjects", [])}
            for e in new_gmail.get("unread_subjects", []):
                if e["id"] not in old_ids:
                    changes["info"].append(f"  From: {e['from']} — {e['subject']}")

    # Asana changes
    old_asana = old.get("asana", {})
    new_asana = new.get("asana", {})
    if "error" not in new_asana:
        new_overdue = new_asana.get("overdue_count", 0)
        if new_overdue > 0:
            changes["urgent"].append(f"{new_overdue} overdue Asana task(s)")
            for t in new_asana.get("overdue_tasks", [])[:3]:
                changes["urgent"].append(f"  - {t['name']} (due {t['due_on']})")

        new_upcoming = new_asana.get("upcoming_count", 0)
        old_upcoming = old_asana.get("upcoming_count", 0)
        if new_upcoming > old_upcoming:
            changes["info"].append(f"{new_upcoming - old_upcoming} new upcoming deadline(s)")

    return changes


# ─── Habits Check ────────────────────────────────────────────────

def check_habits() -> list[str]:
    """Check HABITS.md for unchecked pillars. Late-day nudge if after 17:00 IST."""
    habits_path = VAULT_DIR / "HABITS.md"
    if not habits_path.exists():
        return []

    now = datetime.now(IST)
    is_late = now.hour >= 17

    if not is_late:
        return []

    try:
        content = habits_path.read_text()
        unchecked = []
        for line in content.split("\n"):
            if line.strip().startswith("- [ ] **"):
                # Extract pillar name
                pillar = line.split("**")[1] if "**" in line else line.strip()
                unchecked.append(pillar)

        if unchecked:
            return [f"Late-day nudge: {len(unchecked)} unchecked habit pillar(s): {', '.join(unchecked)}"]
    except Exception as e:
        log(f"Habits check failed: {e}")

    return []


# ─── Draft Management ────────────────────────────────────────────

def expire_old_drafts():
    """Move drafts older than 24h from active/ to expired/."""
    active_dir = VAULT_DIR / "drafts" / "active"
    expired_dir = VAULT_DIR / "drafts" / "expired"

    if not active_dir.exists():
        return

    expired_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    cutoff = now - timedelta(hours=24)

    for draft_file in active_dir.glob("*.md"):
        try:
            # Check file modification time as proxy for creation time
            mtime = datetime.fromtimestamp(draft_file.stat().st_mtime)
            if mtime < cutoff:
                dest = expired_dir / draft_file.name
                draft_file.rename(dest)
                log(f"Expired draft: {draft_file.name}")
        except Exception as e:
            log(f"Failed to expire draft {draft_file.name}: {e}")


# ─── LLM Reasoning (Optional) ───────────────────────────────────

def reason_with_claude(changes: dict, snapshot: dict) -> str | None:
    """Use Claude to reason over changes and generate actionable insights."""
    try:
        from claude_client import create_message

        # Load SOUL.md for personality
        soul_path = VAULT_DIR / "SOUL.md"
        soul = soul_path.read_text() if soul_path.exists() else ""

        prompt = f"""You are Vidit's Second Brain heartbeat. Here is what changed since the last check:

**Urgent items:**
{chr(10).join(changes.get('urgent', ['None'])) }

**Info:**
{chr(10).join(changes.get('info', ['None']))}

**Current snapshot summary:**
- Gmail: {snapshot.get('gmail', {}).get('unread_count', '?')} unread
- Asana: {snapshot.get('asana', {}).get('overdue_count', '?')} overdue, {snapshot.get('asana', {}).get('upcoming_count', '?')} upcoming
- GitHub: rate limit {snapshot.get('github', {}).get('rate_limit_remaining', '?')} remaining

Provide a brief (3-5 bullet) summary of what Vidit should focus on right now. Be direct and actionable."""

        result = create_message(
            system=soul[:2000] if soul else "You are a concise productivity assistant.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )

        return result

    except Exception as e:
        log(f"Claude reasoning failed: {e}")
        return None


# ─── Daily Log ───────────────────────────────────────────────────

def append_to_daily_log(summary: str):
    """Append heartbeat summary to today's daily log."""
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
    except Exception as e:
        log(f"Failed to write daily log: {e}")


# ─── Main ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Second Brain heartbeat")
    parser.add_argument("--force", action="store_true", help="Run outside active hours")
    parser.add_argument("--no-llm", action="store_true", help="Skip Claude reasoning")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing state")
    args = parser.parse_args()

    # Active hours gate
    if not args.force and not is_active_hours():
        log("Outside active hours (9-21 IST), skipping.")
        return

    log("Heartbeat started")

    # 1. Gather data from all integrations
    snapshot = gather_all()
    log(f"Data gathered: Gmail={snapshot['gmail'].get('unread_count', '?')} unread, "
        f"Asana={snapshot['asana'].get('overdue_count', '?')} overdue")

    # 2. Diff against last state
    old_state = load_state()
    changes = diff_snapshots(old_state, snapshot)

    # 3. Check habits (late-day nudge)
    habit_nudges = check_habits()
    if habit_nudges:
        changes["info"].extend(habit_nudges)

    # 4. Expire old drafts
    expire_old_drafts()

    # 5. Summarize
    all_items = changes["urgent"] + changes["info"]
    has_changes = bool(all_items)

    if args.dry_run:
        print("=== Heartbeat Dry Run ===")
        print(f"Timestamp: {snapshot['timestamp']}")
        print(f"\nUrgent: {changes['urgent'] or ['None']}")
        print(f"Info: {changes['info'] or ['None']}")
        print(f"\nWould notify: {bool(changes['urgent'])}")
        return

    # 6. Claude reasoning (optional)
    llm_summary = None
    if not args.no_llm and has_changes:
        llm_summary = reason_with_claude(changes, snapshot)

    # 7. Build summary for daily log
    summary_parts = []
    if changes["urgent"]:
        summary_parts.append(f"URGENT: {'; '.join(changes['urgent'][:3])}")
    if changes["info"]:
        summary_parts.append(f"Info: {'; '.join(changes['info'][:3])}")
    if not summary_parts:
        summary_parts.append("No changes since last check.")

    summary = " | ".join(summary_parts)

    # 8. Notify for urgent items
    if changes["urgent"]:
        notify_urgent(changes["urgent"])

    # 9. Append to daily log
    if has_changes:
        log_entry = summary
        if llm_summary:
            log_entry += f"\n  Claude: {llm_summary[:200]}"
        append_to_daily_log(log_entry)

    # 10. Save state
    save_state(snapshot)

    log(f"Heartbeat complete. Changes: {len(all_items)}, Urgent: {len(changes['urgent'])}")
    print(f"Heartbeat complete. {len(all_items)} changes detected ({len(changes['urgent'])} urgent).")

    if llm_summary:
        print(f"\nClaude's summary:\n{llm_summary}")


if __name__ == "__main__":
    main()
