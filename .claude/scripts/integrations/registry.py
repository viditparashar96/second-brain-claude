"""
Integration Registry — Tracks available integrations and their status.

Checks which integrations have valid credentials configured.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent)
)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))


@dataclass
class Integration:
    name: str
    description: str
    enabled: bool
    status: str  # "ready", "missing_credentials", "not_configured"


def check_gmail() -> Integration:
    creds_path = os.path.join(PROJECT_DIR, ".claude", "data", "credentials", "gmail", "credentials.json")
    token_path = os.path.join(PROJECT_DIR, ".claude", "data", "credentials", "gmail", "token.json")

    if not os.path.exists(creds_path):
        return Integration("gmail", "Gmail (email)", False, "missing_credentials: credentials.json not found")

    has_token = os.path.exists(token_path)
    return Integration(
        "gmail", "Gmail (email)", True,
        "ready" if has_token else "ready (will need OAuth on first use)"
    )


def check_github() -> Integration:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return Integration("github", "GitHub (code)", False, "missing_credentials: GITHUB_TOKEN not in .env")
    return Integration("github", "GitHub (code)", True, "ready")


def check_asana() -> Integration:
    token = os.environ.get("ASANA_TOKEN", "")
    if not token:
        return Integration("asana", "Asana (tasks)", False, "missing_credentials: ASANA_TOKEN not in .env")
    return Integration("asana", "Asana (tasks)", True, "ready")


def get_all() -> list[Integration]:
    return [check_gmail(), check_github(), check_asana()]


def get_enabled() -> list[Integration]:
    return [i for i in get_all() if i.enabled]


def print_status():
    """Print a formatted status table of all integrations."""
    integrations = get_all()
    print("Integration Status:")
    print("-" * 60)
    for i in integrations:
        icon = "+" if i.enabled else "-"
        print(f"  [{icon}] {i.name:<10} {i.description:<20} {i.status}")
    print("-" * 60)
    enabled = sum(1 for i in integrations if i.enabled)
    print(f"  {enabled}/{len(integrations)} integrations ready")
