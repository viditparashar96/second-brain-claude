"""
Google Calendar CLI subcommands.

Usage:
    gcal events [--today] [--upcoming N] [--date YYYY-MM-DD] [--limit N]
    gcal next [--minutes N]
"""

import argparse

from . import client


def main(args: list[str]):
    parser = argparse.ArgumentParser(
        prog="query.py gcal", description="Google Calendar integration"
    )
    sub = parser.add_subparsers(dest="action", required=True)

    # events
    p_events = sub.add_parser("events", help="List calendar events")
    p_events.add_argument(
        "--today", action="store_true", help="Show today's events (default)"
    )
    p_events.add_argument(
        "--upcoming", type=int, metavar="DAYS", default=0,
        help="Show events for next N days"
    )
    p_events.add_argument(
        "--date", type=str, default="", help="Show events for specific date (YYYY-MM-DD)"
    )
    p_events.add_argument(
        "--limit", type=int, default=50, help="Max results (default: 50)"
    )

    # next — upcoming events within N minutes
    p_next = sub.add_parser("next", help="Show events starting soon")
    p_next.add_argument(
        "--minutes", type=int, default=30,
        help="Look ahead window in minutes (default: 30)"
    )

    parsed = parser.parse_args(args)

    if parsed.action == "events":
        if parsed.date:
            events = client.list_events(date=parsed.date, limit=parsed.limit)
        elif parsed.upcoming > 0:
            events = client.list_events(days=parsed.upcoming, limit=parsed.limit)
        else:
            # Default: today
            events = client.list_events(days=1, limit=parsed.limit)
        print(client.format_event_list(events))

    elif parsed.action == "next":
        events = client.get_upcoming(minutes=parsed.minutes)
        if events:
            print(f"Events in the next {parsed.minutes} minutes:\n")
            print(client.format_event_list(events))
        else:
            print(f"No events in the next {parsed.minutes} minutes.")
