"""
Google Calendar authentication — Reuses Gmail OAuth2 token.

Calendar scope (calendar.readonly) is added during the setup dashboard
OAuth flow alongside gmail.modify. This module reads the shared token
and builds a Calendar API service.
"""

import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Paths — shared with Gmail (same Google OAuth token)
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from config import CREDENTIALS_DIR

CREDENTIALS_PATH = CREDENTIALS_DIR / "gmail" / "credentials.json"
TOKEN_PATH = CREDENTIALS_DIR / "gmail" / "token.json"

# Calendar scope (read-only)
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_credentials() -> Credentials:
    """Get valid Google OAuth2 credentials with calendar scope.

    Reuses the shared Gmail token. If the token doesn't have calendar scope,
    triggers a re-auth flow to add it.
    """
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"Google credentials not found at {CREDENTIALS_PATH}. "
                    "Run the setup dashboard to configure Google integrations."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next use
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

    return creds
