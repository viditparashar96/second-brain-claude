#!/usr/bin/env python3
"""Daily Reflection — Reviews daily log, promotes important items to MEMORY.md, archives habits."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, DAILY_DIR, LOG_DIR, SECOND_BRAIN_HOME

MEMORY_PATH = VAULT_DIR / "MEMORY.md"
HABITS_PATH = VAULT_DIR / "HABITS.md"
IST = timezone(timedelta(hours=5, minutes=30))


def log(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "reflection.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass


def extract_with_claude(daily_content):
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

Each item should be a short string (1-2 sentences). Only include genuinely important items.
Return ONLY valid JSON, no markdown fences."""

        text = create_message(
            system="You extract structured data from daily logs. Return only valid JSON.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        if not text:
            return extract_heuristic(daily_content)
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        return json.loads(text)
    except Exception as e:
        log(f"Claude extraction failed: {e}")
        return extract_heuristic(daily_content)


def extract_heuristic(daily_content):
    result = {"active_projects": [], "key_decisions": [], "client_notes": [],
              "lessons_learned": [], "goals": [], "team_context": []}
    for line in daily_content.split("\n"):
        lower = line.strip().lower()
        if "decision" in lower or "decided" in lower:
            result["key_decisions"].append(line.strip().lstrip("- "))
        elif "learned" in lower or "gotcha" in lower:
            result["lessons_learned"].append(line.strip().lstrip("- "))
        elif "client" in lower or "customer" in lower:
            result["client_notes"].append(line.strip().lstrip("- "))
        elif "goal" in lower or "milestone" in lower:
            result["goals"].append(line.strip().lstrip("- "))
        elif "project" in lower and ("shipped" in lower or "completed" in lower):
            result["active_projects"].append(line.strip().lstrip("- "))
    return result


SECTION_MAP = {
    "active_projects": "## Active Projects",
    "key_decisions": "## Key Decisions",
    "client_notes": "## Client Notes",
    "lessons_learned": "## Lessons Learned",
    "goals": "## Goals",
    "team_context": "## Team Context",
}


def promote_to_memory(extracted, source_date, dry_run=False):
    if not MEMORY_PATH.exists():
        print("MEMORY.md not found")
        return
    content = MEMORY_PATH.read_text()
    additions = {}
    for key, header in SECTION_MAP.items():
        items = extracted.get(key, [])
        if items:
            lines = [f"- {source_date} — {item}" for item in items if item.strip()]
            if lines:
                additions[header] = lines

    if not additions:
        print("Nothing to promote to MEMORY.md")
        return

    if dry_run:
        print("=== Would promote to MEMORY.md ===")
        for section, lines in additions.items():
            print(f"\n{section}:")
            for line in lines:
                print(f"  {line}")
        return

    for header, lines in additions.items():
        insert_text = "\n".join(lines) + "\n"
        if header in content:
            idx = content.index(header) + len(header)
            rest = content[idx:]
            nl = rest.find("\n")
            if nl >= 0:
                pos = idx + nl + 1
                while pos < len(content) and content[pos:pos + 4] in ("\n", "<!--"):
                    next_nl = content.find("\n", pos + 1)
                    if next_nl < 0:
                        break
                    pos = next_nl + 1
                content = content[:pos] + insert_text + content[pos:]
    MEMORY_PATH.write_text(content)
    total = sum(len(v) for v in additions.values())
    print(f"Promoted {total} items to MEMORY.md")


def archive_and_reset_habits(source_date, dry_run=False):
    if not HABITS_PATH.exists():
        return
    content = HABITS_PATH.read_text()
    checklist_lines = []
    in_today = False
    for line in content.split("\n"):
        if re.match(r"^## Today: \d{4}-\d{2}-\d{2}", line):
            in_today = True
            continue
        if in_today:
            if line.startswith("## "):
                break
            if line.strip().startswith("- ["):
                checklist_lines.append(line)

    if not checklist_lines:
        return

    archive = f"\n### {source_date}\n" + "".join(f"{l}\n" for l in checklist_lines)
    today = datetime.now().strftime("%Y-%m-%d")
    fresh = [l.replace("- [x]", "- [ ]").replace("- [X]", "- [ ]") for l in checklist_lines]

    if dry_run:
        print(f"\n=== Would archive habits from {source_date} ===")
        print(archive)
        print(f"\n=== Fresh checklist for {today} ===")
        for l in fresh:
            print(l)
        return

    new_content = re.sub(r"## Today: \d{4}-\d{2}-\d{2}", f"## Today: {today}", content)
    for old, new in zip(checklist_lines, fresh):
        new_content = new_content.replace(old, new, 1)
    if "## History" in new_content:
        idx = new_content.index("## History") + len("## History")
        nl = new_content.find("\n", idx)
        if nl >= 0:
            new_content = new_content[:nl + 1] + archive + new_content[nl + 1:]
    else:
        new_content += f"\n## History\n{archive}"
    HABITS_PATH.write_text(new_content)
    print(f"Habits archived for {source_date}, fresh checklist for {today}")


def main():
    parser = argparse.ArgumentParser(description="Daily reflection")
    parser.add_argument("--date", default="")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.date:
        target = args.date
    else:
        target = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    daily_path = DAILY_DIR / f"{target}.md"
    if not daily_path.exists():
        print(f"No daily log found for {target}")
        return

    content = daily_path.read_text()
    if not content.strip():
        print(f"Daily log for {target} is empty")
        return

    extracted = extract_heuristic(content) if args.no_llm else extract_with_claude(content)
    promote_to_memory(extracted, target, dry_run=args.dry_run)
    archive_and_reset_habits(target, dry_run=args.dry_run)

    if not args.dry_run:
        line_count = MEMORY_PATH.read_text().count("\n") if MEMORY_PATH.exists() else 0
        if line_count > 500:
            print(f"WARNING: MEMORY.md is {line_count} lines — consider pruning")

    print(f"Reflection complete for {target}")


if __name__ == "__main__":
    main()
