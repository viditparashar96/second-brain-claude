"""
Gmail OAuth2 authentication — Desktop app flow.

Handles token creation, refresh, and storage.
Credentials.json comes from Google Cloud Console.
Token.json is auto-generated on first OAuth flow.
"""

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent.parent)
)

CREDENTIALS_PATH = os.path.join(PROJECT_DIR, ".claude", "data", "credentials", "gmail", "credentials.json")
TOKEN_PATH = os.path.join(PROJECT_DIR, ".claude", "data", "credentials", "gmail", "token.json")

# gmail.modify covers: list, read, compose drafts, send (no permanent delete)
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_credentials() -> Credentials:
    """Get valid Gmail OAuth2 credentials, refreshing or re-authorizing as needed."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Gmail credentials not found at {CREDENTIALS_PATH}. "
                    "Download from Google Cloud Console → APIs & Services → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next use
        Path(TOKEN_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds
