"""
Gmail CLI subcommands.

Usage:
    gmail list [--unread] [--limit N]
    gmail read <message_id>
    gmail search "<query>"
    gmail draft --to <addr> --subject <subj> --body <text> [--reply-to <id>]
"""

import argparse
import sys

from . import client


def main(args: list[str]):
    parser = argparse.ArgumentParser(prog="query.py gmail", description="Gmail integration")
    sub = parser.add_subparsers(dest="action", required=True)

    # list
    p_list = sub.add_parser("list", help="List recent emails")
    p_list.add_argument("--unread", action="store_true", help="Only unread emails")
    p_list.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")

    # read
    p_read = sub.add_parser("read", help="Read a single email")
    p_read.add_argument("message_id", help="Gmail message ID")

    # search
    p_search = sub.add_parser("search", help="Search emails with Gmail query syntax")
    p_search.add_argument("query", help="Gmail search query (e.g., 'from:boss@co.com')")
    p_search.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")

    # draft
    p_draft = sub.add_parser("draft", help="Create a draft email")
    p_draft.add_argument("--to", required=True, help="Recipient email")
    p_draft.add_argument("--subject", required=True, help="Email subject")
    p_draft.add_argument("--body", required=True, help="Email body text")
    p_draft.add_argument("--reply-to", default="", help="Message ID to reply to (for threading)")

    parsed = parser.parse_args(args)

    if parsed.action == "list":
        emails = client.list_emails(limit=parsed.limit, unread_only=parsed.unread)
        print(client.format_email_list(emails))

    elif parsed.action == "read":
        email_obj = client.read_email(parsed.message_id)
        print(client.format_email_full(email_obj))

    elif parsed.action == "search":
        emails = client.search_emails(parsed.query, limit=parsed.limit)
        print(client.format_email_list(emails))

    elif parsed.action == "draft":
        draft = client.create_draft(
            to=parsed.to,
            subject=parsed.subject,
            body=parsed.body,
            reply_to_id=parsed.reply_to,
        )
        print(f"Draft created: {draft.id}")
        print(f"  To: {draft.to}")
        print(f"  Subject: {draft.subject}")
