#!/usr/bin/env python3
"""Unified Integration CLI — single entry point for all integrations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import registry


def main():
    if len(sys.argv) < 2:
        print("Usage: query.py {status|gmail|github|asana} <subcommand>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        registry.print_status()
    elif command == "gmail":
        from gmail.cli import main as gmail_main
        gmail_main(sys.argv[2:])
    elif command == "github":
        from gh.cli import main as github_main
        github_main(sys.argv[2:])
    elif command == "asana":
        from asana_int.cli import main as asana_main
        asana_main(sys.argv[2:])
    else:
        print(f"Unknown: {command}. Available: gmail, github, asana, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
