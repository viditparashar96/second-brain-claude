#!/usr/bin/env python3
"""
Daily Reflection — Memory consolidation script.

Runs daily at 8:00 AM IST. Reviews yesterday's daily log,
promotes important items to MEMORY.md, archives habits,
and creates a fresh daily checklist.

Usage:
    python memory_reflect.py [--date YYYY-MM-DD] [--no-llm] [--dry-run]

Options:
    --date      Process a specific date (default: yesterday)
    --no-llm    Use heuristic extraction instead of Claude
    --dry-run   Print what would be promoted without writing
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(SCRIPTS_DIR.parent.parent)
)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

VAULT_DIR = Path(PROJECT_DIR) / "Dynamous" / "Memory"
DAILY_DIR = VAULT_DIR / "daily"
MEMORY_PATH = VAULT_DIR / "MEMORY.md"
HABITS_PATH = VAULT_DIR / "HABITS.md"
LOG_FILE = Path(PROJECT_DIR) / ".claude" / "data" / "logs" / "reflection.log"

IST = timezone(timedelta(hours=5, minutes=30))


def log(msg: str):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass


# ─── Extract with Claude ─────────────────────────────────────────

def extract_with_claude(daily_content: str) -> dict:
    """Use Claude to extract promotable items from yesterday's daily log."""
    try:
        from claude_client import create_message

        prompt = f"""Review this daily log and extract items worth promoting to long-term memory.

<daily_log>
{daily_content}
</daily_log>

Return a JSON object with these keys (empty arrays if nothing found):
- "active_projects": items about project status/progress
- "key_decisions": decisions made with context
- "client_notes": client/customer insights
- "lessons_learned": gotchas, mistakes, or insights
- "goals": goal progress or new goals
- "team_context": info about team members, roles, preferences

Each item should be a short string (1-2 sentences). Only include genuinely important items — this goes into MEMORY.md which is loaded into every conversation.

Return ONLY valid JSON, no markdown fences."""

        text = create_message(
            system="You extract structured data from daily logs. Return only valid JSON.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )

        if not text:
            return extract_heuristic(daily_content)

        text = text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        return json.loads(text)

    except Exception as e:
        log(f"Claude extraction failed: {e}, falling back to heuristic")
        return extract_heuristic(daily_content)


def extract_heuristic(daily_content: str) -> dict:
    """Fallback: extract promotable items using keyword heuristics."""
    result = {
        "active_projects": [],
        "key_decisions": [],
        "client_notes": [],
        "lessons_learned": [],
        "goals": [],
        "team_context": [],
    }

    for line in daily_content.split("\n"):
        stripped = line.strip().lower()

        if "decision" in stripped or "decided" in stripped:
            result["key_decisions"].append(line.strip().lstrip("- "))
        elif "learned" in stripped or "gotcha" in stripped or "lesson" in stripped:
            result["lessons_learned"].append(line.strip().lstrip("- "))
        elif "client" in stripped or "customer" in stripped:
            result["client_notes"].append(line.strip().lstrip("- "))
        elif "goal" in stripped or "milestone" in stripped:
            result["goals"].append(line.strip().lstrip("- "))
        elif "project" in stripped and ("shipped" in stripped or "launched" in stripped or "completed" in stripped):
            result["active_projects"].append(line.strip().lstrip("- "))

    return result


# ─── Promote to MEMORY.md ────────────────────────────────────────

SECTION_MAP = {
    "active_projects": "## Active Projects",
    "key_decisions": "## Key Decisions",
    "client_notes": "## Client Notes",
    "lessons_learned": "## Lessons Learned",
    "goals": "## Goals",
    "team_context": "## Team Context",
}


def promote_to_memory(extracted: dict, source_date: str, dry_run: bool = False):
    """Append extracted items to the appropriate sections in MEMORY.md."""
    if not MEMORY_PATH.exists():
        log("MEMORY.md not found, skipping promotion")
        return

    content = MEMORY_PATH.read_text()
    additions = {}

    for key, section_header in SECTION_MAP.items():
        items = extracted.get(key, [])
        if not items:
            continue

        lines = [f"- {source_date} — {item}" for item in items if item.strip()]
        if lines:
            additions[section_header] = lines

    if not additions:
        log("Nothing to promote")
        print("Nothing to promote to MEMORY.md")
        return

    if dry_run:
        print("=== Would promote to MEMORY.md ===")
        for section, lines in additions.items():
            print(f"\n{section}:")
            for line in lines:
                print(f"  {line}")
        return

    # Insert items after each section header
    for section_header, lines in additions.items():
        insert_text = "\n".join(lines) + "\n"
        # Find the section and insert after any existing content or comments
        if section_header in content:
            # Find position after the header line
            idx = content.index(section_header) + len(section_header)
            # Skip past any existing comment line
            rest = content[idx:]
            newline_idx = rest.find("\n")
            if newline_idx >= 0:
                insert_pos = idx + newline_idx + 1
                # Skip blank lines and comments
                while insert_pos < len(content) and content[insert_pos:insert_pos + 4] in ("\n", "<!--"):
                    next_newline = content.find("\n", insert_pos + 1)
                    if next_newline < 0:
                        break
                    insert_pos = next_newline + 1

                content = content[:insert_pos] + insert_text + content[insert_pos:]

    MEMORY_PATH.write_text(content)
    total_items = sum(len(v) for v in additions.values())
    log(f"Promoted {total_items} items to MEMORY.md")
    print(f"Promoted {total_items} items to MEMORY.md")


# ─── Habits Archive ──────────────────────────────────────────────

def archive_and_reset_habits(source_date: str, dry_run: bool = False):
    """Archive yesterday's habit checklist to History and create a fresh one for today."""
    if not HABITS_PATH.exists():
        return

    content = HABITS_PATH.read_text()

    # Extract today's checklist lines
    checklist_lines = []
    in_today = False
    today_header_pattern = re.compile(r"^## Today: \d{4}-\d{2}-\d{2}")

    for line in content.split("\n"):
        if today_header_pattern.match(line):
            in_today = True
            continue
        if in_today:
            if line.startswith("## "):
                break
            if line.strip().startswith("- ["):
                checklist_lines.append(line)

    if not checklist_lines:
        log("No habit checklist found to archive")
        return

    # Build archive entry
    archive_entry = f"\n### {source_date}\n"
    for line in checklist_lines:
        archive_entry += f"{line}\n"

    # Build fresh checklist for today
    today = datetime.now(IST).strftime("%Y-%m-%d")
    fresh_lines = []
    for line in checklist_lines:
        # Reset checkboxes to unchecked
        fresh_lines.append(line.replace("- [x]", "- [ ]").replace("- [X]", "- [ ]"))

    if dry_run:
        print(f"\n=== Would archive habits from {source_date} ===")
        print(archive_entry)
        print(f"\n=== Would create fresh checklist for {today} ===")
        for line in fresh_lines:
            print(line)
        return

    # Update the file
    # Replace today's date header
    new_content = re.sub(
        r"## Today: \d{4}-\d{2}-\d{2}",
        f"## Today: {today}",
        content,
    )

    # Replace checklist lines with fresh ones
    for old_line, new_line in zip(checklist_lines, fresh_lines):
        new_content = new_content.replace(old_line, new_line, 1)

    # Append archive entry before the end of History section
    if "## History" in new_content:
        history_idx = new_content.index("## History") + len("## History")
        # Find the next line after the header
        next_newline = new_content.find("\n", history_idx)
        if next_newline >= 0:
            insert_pos = next_newline + 1
            new_content = new_content[:insert_pos] + archive_entry + new_content[insert_pos:]
    else:
        new_content += f"\n## History\n{archive_entry}"

    HABITS_PATH.write_text(new_content)
    log(f"Archived habits for {source_date}, created fresh checklist for {today}")
    print(f"Habits archived for {source_date}, fresh checklist for {today}")


# ─── Prune MEMORY.md ─────────────────────────────────────────────

def prune_memory_if_needed(max_lines: int = 500):
    """Warn if MEMORY.md exceeds the line limit."""
    if not MEMORY_PATH.exists():
        return

    content = MEMORY_PATH.read_text()
    line_count = content.count("\n")

    if line_count > max_lines:
        log(f"WARNING: MEMORY.md is {line_count} lines (limit {max_lines}). Needs pruning.")
        print(f"WARNING: MEMORY.md is {line_count} lines — consider pruning to stay under {max_lines}.")


# ─── Main ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily reflection / memory consolidation")
    parser.add_argument("--date", default="", help="Date to process (YYYY-MM-DD, default: yesterday)")
    parser.add_argument("--no-llm", action="store_true", help="Use heuristic extraction")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    args = parser.parse_args()

    # Determine which date to process
    if args.date:
        target_date = args.date
    else:
        yesterday = datetime.now(IST) - timedelta(days=1)
        target_date = yesterday.strftime("%Y-%m-%d")

    log(f"Reflection started for {target_date}")

    # Read the daily log
    daily_path = DAILY_DIR / f"{target_date}.md"
    if not daily_path.exists():
        log(f"No daily log found for {target_date}")
        print(f"No daily log found for {target_date}")
        return

    daily_content = daily_path.read_text()
    if not daily_content.strip():
        print(f"Daily log for {target_date} is empty")
        return

    # Extract items
    if args.no_llm:
        extracted = extract_heuristic(daily_content)
    else:
        extracted = extract_with_claude(daily_content)

    # Promote to MEMORY.md
    promote_to_memory(extracted, target_date, dry_run=args.dry_run)

    # Archive and reset habits
    archive_and_reset_habits(target_date, dry_run=args.dry_run)

    # Check MEMORY.md size
    if not args.dry_run:
        prune_memory_if_needed()

    log(f"Reflection complete for {target_date}")
    print(f"Reflection complete for {target_date}")


if __name__ == "__main__":
    main()
