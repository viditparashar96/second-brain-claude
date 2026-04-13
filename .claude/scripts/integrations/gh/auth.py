"""
GitHub authentication — Fine-grained Personal Access Token.

Token stored in .env as GITHUB_TOKEN.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from github import Auth, Github

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent)
)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))


def get_client() -> Github:
    """Authenticate and return a PyGithub client."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN not set. Add it to .env file. "
            "Create at: GitHub Settings > Developer settings > Personal access tokens > Fine-grained tokens"
        )
    auth = Auth.Token(token)
    return Github(auth=auth)
