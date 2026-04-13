"""
Asana authentication — Personal Access Token.

Token stored in .env as ASANA_TOKEN.
"""

import os
from pathlib import Path

import asana
from dotenv import load_dotenv

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent)
)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))


def get_api_client() -> asana.ApiClient:
    """Authenticate and return an Asana API client (SDK v5)."""
    token = os.environ.get("ASANA_TOKEN", "")
    if not token:
        raise ValueError(
            "ASANA_TOKEN not set. Add it to .env file. "
            "Create at: https://app.asana.com/0/developer-console"
        )

    configuration = asana.Configuration()
    configuration.access_token = token
    # Enable deprecation headers proactively
    configuration.default_headers = {
        "asana-enable": "new_goal_memberships,new_project_templates,new_sections"
    }

    return asana.ApiClient(configuration)
