#!/usr/bin/env python3
"""
Unified Integration CLI — Single entry point for all integrations.

Usage:
    python query.py status                          # Show integration status
    python query.py gmail list [--unread] [--limit N]
    python query.py gmail read <message_id>
    python query.py gmail search "<query>"
    python query.py gmail draft --to <addr> --subject <subj> --body <text>
    python query.py github prs [--repo owner/repo] [--state open]
    python query.py github issues [--repo owner/repo]
    python query.py github diff <pr_number> [--repo owner/repo]
    python query.py github review <pr_number> --body <text>
    python query.py asana tasks [--project <gid>]
    python query.py asana overdue
    python query.py asana upcoming [--days N]
    python query.py asana projects
"""

import sys
from pathlib import Path

# Add parent dirs to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import registry


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        registry.print_status()
        return

    if command == "gmail":
        from gmail.cli import main as gmail_main
        gmail_main(sys.argv[2:])
    elif command == "github":
        from gh.cli import main as github_main
        github_main(sys.argv[2:])
    elif command == "asana":
        from asana_int.cli import main as asana_main
        asana_main(sys.argv[2:])
    else:
        print(f"Unknown integration: {command}")
        print("Available: gmail, github, asana, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
