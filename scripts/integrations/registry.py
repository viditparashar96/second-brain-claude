"""Integration Registry — Tracks available integrations and their status."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import SECOND_BRAIN_HOME, CREDENTIALS_DIR

# Load .env from second-brain home
_env_path = SECOND_BRAIN_HOME / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(str(_env_path))


@dataclass
class Integration:
    name: str
    description: str
    enabled: bool
    status: str


def check_gmail():
    creds = CREDENTIALS_DIR / "gmail" / "credentials.json"
    token = CREDENTIALS_DIR / "gmail" / "token.json"
    if not creds.exists():
        return Integration("gmail", "Gmail (email)", False, "missing credentials.json")
    return Integration("gmail", "Gmail (email)", True,
                       "ready" if token.exists() else "ready (OAuth on first use)")


def check_github():
    if not os.environ.get("GITHUB_TOKEN"):
        return Integration("github", "GitHub (code)", False, "GITHUB_TOKEN not set")
    return Integration("github", "GitHub (code)", True, "ready")


def check_asana():
    if not os.environ.get("ASANA_TOKEN"):
        return Integration("asana", "Asana (tasks)", False, "ASANA_TOKEN not set")
    return Integration("asana", "Asana (tasks)", True, "ready")


def check_gcal():
    token = CREDENTIALS_DIR / "gmail" / "token.json"
    if not token.exists():
        return Integration("gcal", "Google Calendar", False, "not authenticated")
    # Check if calendar scope is in the token
    try:
        import json
        data = json.loads(token.read_text())
        scopes = data.get("scopes", [])
        if any("calendar" in s for s in scopes):
            return Integration("gcal", "Google Calendar", True, "ready")
        return Integration("gcal", "Google Calendar", False, "calendar scope not granted")
    except Exception:
        return Integration("gcal", "Google Calendar", False, "token unreadable")


def get_all():
    return [check_gmail(), check_gcal(), check_github(), check_asana()]


def get_enabled():
    return [i for i in get_all() if i.enabled]


def print_status():
    integrations = get_all()
    print("Integration Status:")
    print("-" * 60)
    for i in integrations:
        icon = "+" if i.enabled else "-"
        print(f"  [{icon}] {i.name:<10} {i.description:<20} {i.status}")
    print("-" * 60)
    print(f"  {sum(1 for i in integrations if i.enabled)}/{len(integrations)} ready")
