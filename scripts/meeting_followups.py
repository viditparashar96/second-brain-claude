#!/usr/bin/env python3
"""
Meeting Follow-up Tracker — Scans meeting notes for overdue action items.

Used by heartbeat to surface unresolved items in daily briefs.

Usage:
    python3 meeting_followups.py [--days N] [--format json|text]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, MEETINGS_DIR


def parse_action_items(filepath: Path) -> list[dict]:
    """Extract unchecked action items from a meeting notes file."""
    items = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return items

    # Extract meeting title from first heading
    title = filepath.stem
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Find unchecked items: - [ ] {action} — **{owner}** — due {date}
    pattern = re.compile(
        r"^- \[ \]\s+(.+?)(?:\s*—\s*\*\*(.+?)\*\*)?(?:\s*—\s*due\s+(\d{4}-\d{2}-\d{2}))?$",
        re.MULTILINE,
    )

    for match in pattern.finditer(content):
        action = match.group(1).strip()
        owner = match.group(2).strip() if match.group(2) else ""
        due_date = match.group(3) if match.group(3) else ""

        items.append({
            "action": action,
            "owner": owner,
            "due_date": due_date,
            "meeting_file": filepath.name,
            "meeting_title": title,
        })

    return items


def get_all_action_items(days: int = 30) -> list[dict]:
    """Get all unchecked action items from recent meeting notes."""
    if not MEETINGS_DIR.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    all_items = []

    for f in sorted(MEETINGS_DIR.glob("*.md"), reverse=True):
        # Parse date from filename (YYYY-MM-DD-topic.md)
        try:
            date_str = f.stem[:10]
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                continue
        except ValueError:
            continue

        all_items.extend(parse_action_items(f))

    return all_items


def get_overdue_items() -> list[dict]:
    """Get action items that are past their due date."""
    today = datetime.now().strftime("%Y-%m-%d")
    all_items = get_all_action_items()

    overdue = []
    for item in all_items:
        if item["due_date"] and item["due_date"] < today:
            overdue.append(item)

    return overdue


def get_due_today() -> list[dict]:
    """Get action items due today."""
    today = datetime.now().strftime("%Y-%m-%d")
    all_items = get_all_action_items()

    return [item for item in all_items if item["due_date"] == today]


def get_upcoming_items(days: int = 7) -> list[dict]:
    """Get action items due within the next N days."""
    today = datetime.now().strftime("%Y-%m-%d")
    cutoff = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    all_items = get_all_action_items()

    return [
        item for item in all_items
        if item["due_date"] and today <= item["due_date"] <= cutoff
    ]


def format_items_text(items: list[dict], label: str = "Action Items") -> str:
    """Format action items for display."""
    if not items:
        return f"No {label.lower()} found."

    lines = [f"{label} ({len(items)}):"]
    for item in items:
        owner_str = f" [{item['owner']}]" if item["owner"] else ""
        due_str = f" (due {item['due_date']})" if item["due_date"] else ""
        lines.append(f"  - {item['action']}{owner_str}{due_str}")
        lines.append(f"    from: {item['meeting_file']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Meeting follow-up tracker")
    parser.add_argument("--days", type=int, default=30, help="Look back N days (default: 30)")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--overdue", action="store_true", help="Show only overdue items")
    parser.add_argument("--today", action="store_true", help="Show items due today")
    parser.add_argument("--upcoming", type=int, metavar="DAYS", help="Show items due in next N days")
    args = parser.parse_args()

    if args.overdue:
        items = get_overdue_items()
        label = "Overdue Items"
    elif args.today:
        items = get_due_today()
        label = "Due Today"
    elif args.upcoming:
        items = get_upcoming_items(days=args.upcoming)
        label = f"Due in Next {args.upcoming} Days"
    else:
        items = get_all_action_items(days=args.days)
        label = "Open Action Items"

    if args.format == "json":
        print(json.dumps(items, indent=2))
    else:
        print(format_items_text(items, label))


if __name__ == "__main__":
    main()
