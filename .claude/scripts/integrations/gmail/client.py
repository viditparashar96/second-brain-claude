"""
Gmail API client — List, read, search, and draft emails.

Uses google-api-python-client. Auth handled by auth.py.
The LLM never sees credentials — only formatted email data.
"""

import base64
import email.utils
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage

from googleapiclient.discovery import build

from .auth import get_credentials


@dataclass
class Email:
    id: str
    thread_id: str
    subject: str
    sender: str
    to: str
    date: str
    snippet: str
    body: str = ""
    labels: list[str] | None = None


@dataclass
class Draft:
    id: str
    message_id: str
    subject: str
    to: str


def get_service():
    """Build and return the Gmail API service."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def _parse_headers(headers: list[dict]) -> dict[str, str]:
    """Extract common headers from Gmail message headers list."""
    result = {}
    for h in headers:
        name = h.get("name", "").lower()
        if name in ("subject", "from", "to", "date"):
            result[name] = h.get("value", "")
    return result


def _extract_body(payload: dict) -> str:
    """Extract plain text body from Gmail message payload."""
    # Simple message
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    # Multipart message — find text/plain part
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        # Nested multipart
        if part.get("parts"):
            for subpart in part["parts"]:
                if subpart.get("mimeType") == "text/plain" and subpart.get("body", {}).get("data"):
                    return base64.urlsafe_b64decode(subpart["body"]["data"]).decode("utf-8", errors="replace")

    # Fallback: try text/html
    for part in parts:
        if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
            return "[HTML content — plain text not available]"

    return "[No readable body]"


def _parse_message(msg: dict, include_body: bool = False) -> Email:
    """Parse a raw Gmail API message into an Email dataclass."""
    payload = msg.get("payload", {})
    headers = _parse_headers(payload.get("headers", []))

    body = ""
    if include_body:
        body = _extract_body(payload)

    return Email(
        id=msg["id"],
        thread_id=msg.get("threadId", ""),
        subject=headers.get("subject", "(no subject)"),
        sender=headers.get("from", ""),
        to=headers.get("to", ""),
        date=headers.get("date", ""),
        snippet=msg.get("snippet", ""),
        body=body,
        labels=msg.get("labelIds", []),
    )


def list_emails(limit: int = 20, unread_only: bool = False, query: str = "") -> list[Email]:
    """List recent emails. Returns Email objects with snippets (no full body)."""
    service = get_service()
    q = query
    if unread_only:
        q = f"is:unread {q}".strip()

    results = service.users().messages().list(
        userId="me", q=q or None, maxResults=min(limit, 100)
    ).execute()

    message_ids = results.get("messages", [])
    if not message_ids:
        return []

    # Fetch metadata for each message (messages.list only returns IDs)
    emails = []
    for msg_ref in message_ids[:limit]:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["Subject", "From", "To", "Date"]
        ).execute()
        emails.append(_parse_message(msg))

    return emails


def read_email(message_id: str) -> Email:
    """Read a single email with full body content."""
    service = get_service()
    msg = service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()
    return _parse_message(msg, include_body=True)


def search_emails(gmail_query: str, limit: int = 20) -> list[Email]:
    """Search emails using Gmail query syntax (e.g., 'from:boss@co.com after:2025/01/01')."""
    return list_emails(limit=limit, query=gmail_query)


def create_draft(to: str, subject: str, body: str, reply_to_id: str = "") -> Draft:
    """Create a Gmail draft (never sends). Returns the draft ID."""
    service = get_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject

    if reply_to_id:
        # Fetch the original message to get headers for threading
        original = service.users().messages().get(
            userId="me", id=reply_to_id, format="metadata",
            metadataHeaders=["Message-ID", "Subject"]
        ).execute()
        orig_headers = _parse_headers(original.get("payload", {}).get("headers", []))
        # Thread the reply
        for h in original.get("payload", {}).get("headers", []):
            if h["name"].lower() == "message-id":
                message["In-Reply-To"] = h["value"]
                message["References"] = h["value"]

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft_body = {"message": {"raw": encoded}}
    if reply_to_id:
        # Thread with original message's thread
        original_full = service.users().messages().get(
            userId="me", id=reply_to_id, format="minimal"
        ).execute()
        draft_body["message"]["threadId"] = original_full.get("threadId", "")

    result = service.users().drafts().create(userId="me", body=draft_body).execute()

    return Draft(
        id=result["id"],
        message_id=result["message"]["id"],
        subject=subject,
        to=to,
    )


def format_email_list(emails: list[Email]) -> str:
    """Format email list for context injection or display."""
    if not emails:
        return "No emails found."

    lines = []
    for e in emails:
        unread = "*" if e.labels and "UNREAD" in e.labels else " "
        lines.append(f"[{unread}] {e.id}  {e.date}")
        lines.append(f"    From: {e.sender}")
        lines.append(f"    Subject: {e.subject}")
        lines.append(f"    {e.snippet[:100]}")
        lines.append("")

    return "\n".join(lines)


def format_email_full(email_obj: Email) -> str:
    """Format a single email for full display."""
    lines = [
        f"ID: {email_obj.id}",
        f"From: {email_obj.sender}",
        f"To: {email_obj.to}",
        f"Date: {email_obj.date}",
        f"Subject: {email_obj.subject}",
        "",
        email_obj.body,
    ]
    return "\n".join(lines)
