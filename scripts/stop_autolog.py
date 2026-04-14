#!/usr/bin/env python3
"""
Stop Hook — Intelligent auto-memory manager.

After every Claude response, this hook:
1. Extracts important items (decisions, action items, facts)
2. Detects NEW entities (projects, clients, team members)
3. Auto-creates vault files for new entities
4. Logs everything to the daily log

Uses Claude CLI (free with Claude Max) for intelligent extraction.
Falls back to heuristics if CLI unavailable.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, DAILY_DIR, LOG_DIR, PROJECTS_DIR, CLIENTS_DIR, TEAM_DIR, RESEARCH_DIR, get_memory_level

CLAUDE_CLI = shutil.which("claude")


def log_msg(msg):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "hooks.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] stop-autolog: {msg}\n")
    except Exception:
        pass


def slugify(name):
    """Convert a name to a file-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')[:50]


def extract_with_cli(text):
    """Use Claude CLI to extract memory items and detect entities."""
    if not CLAUDE_CLI:
        return None

    prompt = f"""Analyze this conversation and extract TWO things as JSON:

1. "log_items": Array of important items (decisions, action items, key facts). Short strings, 1 line each. Empty array if nothing noteworthy.

2. "entities": Array of newly mentioned entities that should be tracked. Each entity is an object with:
   - "type": "project" | "client" | "team" | "research"
   - "name": The entity name (e.g., "School Cab", "Airtel Africa", "Priya")
   - "context": One sentence describing it

Only include entities that are clearly defined (not just casually mentioned). Return empty array if none.

ONLY return valid JSON, nothing else:
{{"log_items": [...], "entities": [...]}}

Conversation:
{text[:4000]}"""

    try:
        result = subprocess.run(
            [CLAUDE_CLI, "--print", "-p", prompt],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            return None

        output = result.stdout.strip()
        # Find JSON object in response
        match = re.search(r'\{.*\}', output, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log_msg(f"CLI extraction failed: {e}")

    return None


def extract_heuristic(text):
    """Fallback: extract using keyword matching (no entity detection)."""
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()

        is_important = (
            "decided" in lower or "decision:" in lower or
            "action item" in lower or "todo:" in lower or
            "created file" in lower or "created draft" in lower or
            "saved to" in lower
        )

        if is_important:
            clean = stripped.lstrip("#-* ").strip()
            if len(clean) > 15 and clean not in items:
                items.append(clean[:200])

    return {"log_items": items[:5], "entities": []}


def create_entity_file(entity):
    """Create a vault file for a newly detected entity."""
    entity_type = entity.get("type", "")
    name = entity.get("name", "")
    context = entity.get("context", "")

    if not name or not entity_type:
        return None

    slug = slugify(name)
    if not slug:
        return None

    type_map = {
        "project": PROJECTS_DIR,
        "client": CLIENTS_DIR,
        "team": TEAM_DIR,
        "research": RESEARCH_DIR,
    }

    target_dir = type_map.get(entity_type)
    if not target_dir:
        return None

    file_path = target_dir / f"{slug}.md"

    # Don't overwrite existing files
    if file_path.exists():
        return None

    target_dir.mkdir(parents=True, exist_ok=True)

    # Generate content based on type
    today = datetime.now().strftime("%Y-%m-%d")

    if entity_type == "project":
        content = f"""# {name}

**Status:** Planning
**Created:** {today}

## Overview

{context}

## Notes

"""
    elif entity_type == "client":
        content = f"""# {name}

**Created:** {today}

## Overview

{context}

## Key Contacts

## Notes

"""
    elif entity_type == "team":
        content = f"""# {name}

**Created:** {today}

## Role

{context}

## Notes

"""
    elif entity_type == "research":
        content = f"""# {name}

**Created:** {today}

## Summary

{context}

## Key Findings

## References

"""
    else:
        return None

    try:
        file_path.write_text(content)
        log_msg(f"Auto-created: {entity_type}/{slug}.md")
        return f"{entity_type}/{slug}.md"
    except Exception as e:
        log_msg(f"Failed to create {entity_type}/{slug}.md: {e}")
        return None


def append_to_daily(items, created_files):
    """Append extracted items and created files to today's daily log."""
    if not items and not created_files:
        return

    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = DAILY_DIR / f"{today}.md"
    now = datetime.now().strftime("%H:%M")

    entry_lines = []

    if items:
        entry_lines.append(f"- **{now}** — [auto] {items[0]}")
        for item in items[1:]:
            entry_lines.append(f"  - {item}")

    for cf in created_files:
        entry_lines.append(f"- **{now}** — [auto-created] [[{cf}]]")

    if not entry_lines:
        return

    entry = "\n".join(entry_lines) + "\n"

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
        log_msg(f"Failed to write daily log: {e}")


def main():
    # Check memory level — only run on "full" mode
    memory_level = get_memory_level()
    if memory_level != "full":
        sys.exit(0)

    try:
        input_data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    last_message = input_data.get("last_assistant_message", "")
    if not last_message:
        content = input_data.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    last_message += block.get("text", "") + "\n"

    if not last_message or len(last_message) < 50:
        sys.exit(0)

    # Extract items and entities
    result = extract_with_cli(last_message)
    if result is None:
        result = extract_heuristic(last_message)

    log_items = result.get("log_items", [])
    entities = result.get("entities", [])

    # Auto-create entity files
    created_files = []
    for entity in entities:
        created = create_entity_file(entity)
        if created:
            created_files.append(created)

    # Log to daily
    if isinstance(log_items, list):
        log_items = [str(item)[:200] for item in log_items if item][:5]
    else:
        log_items = []

    append_to_daily(log_items, created_files)
    sys.exit(0)


if __name__ == "__main__":
    main()
