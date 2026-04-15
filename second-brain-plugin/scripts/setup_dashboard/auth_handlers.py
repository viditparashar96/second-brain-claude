"""
Auth Handlers — OAuth flows and token verification for setup dashboard.

Handles:
- Gmail OAuth2 (Desktop app flow via redirect)
- Google Calendar OAuth2 (shared flow with Gmail, adds calendar scope)
- GitHub PAT verification
- Asana PAT verification
"""

import json
import os
import sys
from pathlib import Path

# Resolve paths
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from config import SECOND_BRAIN_HOME, CREDENTIALS_DIR, DATA_DIR

# .env path
ENV_PATH = SECOND_BRAIN_HOME / ".env"

# Gmail/Calendar OAuth paths
GMAIL_CREDS_DIR = CREDENTIALS_DIR / "gmail"
GMAIL_CREDENTIALS_PATH = GMAIL_CREDS_DIR / "credentials.json"
GMAIL_TOKEN_PATH = GMAIL_CREDS_DIR / "token.json"

# Shipped OAuth client ID (bundled with plugin)
SHIPPED_OAUTH_CLIENT = PLUGIN_ROOT / "data" / "google_oauth_client.json"

# Scopes
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
COMBINED_GOOGLE_SCOPES = GMAIL_SCOPES + CALENDAR_SCOPES

DASHBOARD_PORT = 3141
REDIRECT_URI = f"http://localhost:{DASHBOARD_PORT}/api/auth/google/callback"

# Store the active OAuth flow so PKCE code_verifier persists across request/callback
_active_google_flow = None


def _get_google_credentials_path() -> Path:
    """Return path to Google OAuth client credentials.

    Priority: user-provided > shipped with plugin.
    """
    if GMAIL_CREDENTIALS_PATH.exists():
        return GMAIL_CREDENTIALS_PATH
    if SHIPPED_OAUTH_CLIENT.exists():
        return SHIPPED_OAUTH_CLIENT
    raise FileNotFoundError(
        "No Google OAuth credentials found. "
        f"Place credentials.json at {GMAIL_CREDENTIALS_PATH} "
        "or ensure the plugin ships with google_oauth_client.json"
    )


def get_google_auth_url(scopes: list[str] | None = None) -> str:
    """Generate Google OAuth authorization URL.

    Stores the Flow object in _active_google_flow so the PKCE code_verifier
    persists when handle_google_callback exchanges the code.
    """
    global _active_google_flow
    from google_auth_oauthlib.flow import Flow

    creds_path = _get_google_credentials_path()
    target_scopes = scopes or COMBINED_GOOGLE_SCOPES

    flow = Flow.from_client_secrets_file(
        str(creds_path),
        scopes=target_scopes,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    _active_google_flow = flow
    return auth_url


def handle_google_callback(authorization_code: str, scopes: list[str] | None = None) -> dict:
    """Exchange authorization code for tokens and save them.

    Reuses the Flow object from get_google_auth_url so the PKCE
    code_verifier matches the one sent during authorization.
    """
    global _active_google_flow

    if _active_google_flow is None:
        # Fallback: create new flow (won't have PKCE verifier, but try anyway)
        from google_auth_oauthlib.flow import Flow
        creds_path = _get_google_credentials_path()
        target_scopes = scopes or COMBINED_GOOGLE_SCOPES
        _active_google_flow = Flow.from_client_secrets_file(
            str(creds_path),
            scopes=target_scopes,
            redirect_uri=REDIRECT_URI,
        )

    flow = _active_google_flow
    _active_google_flow = None  # Clear after use
    flow.fetch_token(code=authorization_code)
    creds = flow.credentials

    # Save token
    GMAIL_CREDS_DIR.mkdir(parents=True, exist_ok=True)
    GMAIL_TOKEN_PATH.write_text(creds.to_json())

    # Copy shipped credentials to user dir if using shipped client
    if not GMAIL_CREDENTIALS_PATH.exists() and SHIPPED_OAUTH_CLIENT.exists():
        import shutil
        shutil.copy2(str(SHIPPED_OAUTH_CLIENT), str(GMAIL_CREDENTIALS_PATH))

    # Determine which services were authorized
    granted = creds.scopes or target_scopes
    services = []
    if any("gmail" in s for s in granted):
        services.append("gmail")
    if any("calendar" in s for s in granted):
        services.append("gcal")

    return {"status": "connected", "services": services}


def verify_gmail() -> dict:
    """Check if Gmail is connected and working."""
    try:
        if not GMAIL_TOKEN_PATH.exists():
            return {"connected": False, "error": "Not authenticated"}

        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN_PATH))
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            GMAIL_TOKEN_PATH.write_text(creds.to_json())

        if not creds.valid:
            return {"connected": False, "error": "Token invalid"}

        # Quick API check
        from googleapiclient.discovery import build
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        return {"connected": True, "email": profile.get("emailAddress", "")}
    except Exception as e:
        return {"connected": False, "error": str(e)}


def verify_gcal() -> dict:
    """Check if Google Calendar is connected and working."""
    try:
        if not GMAIL_TOKEN_PATH.exists():
            return {"connected": False, "error": "Not authenticated"}

        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN_PATH))
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            GMAIL_TOKEN_PATH.write_text(creds.to_json())

        # Check if calendar scope is granted
        granted = creds.scopes or []
        if not any("calendar" in s for s in granted):
            return {"connected": False, "error": "Calendar scope not granted"}

        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        calendars = service.calendarList().list(maxResults=1).execute()
        return {"connected": True, "calendars": len(calendars.get("items", []))}
    except Exception as e:
        return {"connected": False, "error": str(e)}


def verify_github(token: str) -> dict:
    """Verify a GitHub PAT by checking rate limit."""
    try:
        from github import Auth, Github
        auth = Auth.Token(token)
        g = Github(auth=auth)
        rate = g.get_rate_limit()
        user = g.get_user()
        return {
            "connected": True,
            "username": user.login,
            "rate_remaining": rate.core.remaining,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


def verify_asana(token: str) -> dict:
    """Verify an Asana PAT by listing workspaces."""
    try:
        import asana
        configuration = asana.Configuration()
        configuration.access_token = token
        client = asana.ApiClient(configuration)
        users_api = asana.UsersApi(client)
        me = users_api.get_user("me", opts={})
        return {
            "connected": True,
            "name": me.get("name", ""),
            "email": me.get("email", ""),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


def save_token_to_env(key: str, value: str):
    """Save or update a token in ~/.second-brain/.env"""
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    found = False

    if ENV_PATH.exists():
        lines = ENV_PATH.read_text().splitlines()
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                found = True
                break

    if not found:
        lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(lines) + "\n")

    # Also set in current process
    os.environ[key] = value
