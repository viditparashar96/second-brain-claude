"""
Google Calendar API client — List and query calendar events.

Read-only. Uses google-api-python-client. Auth handled by auth.py.
The LLM never sees credentials — only formatted event data.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build

from .auth import get_credentials


@dataclass
class CalendarEvent:
    id: str
    summary: str
    start: datetime
    end: datetime
    attendees: list[str] = field(default_factory=list)
    location: str = ""
    meet_link: str = ""
    description: str = ""
    calendar_name: str = ""
    status: str = ""
    organizer: str = ""


def get_service():
    """Build and return the Google Calendar API service."""
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


def _parse_datetime(dt_info: dict) -> datetime:
    """Parse a Google Calendar datetime object."""
    if "dateTime" in dt_info:
        dt_str = dt_info["dateTime"]
        # Handle timezone offset format
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            # Fallback for edge cases
            return datetime.now(timezone.utc)
    elif "date" in dt_info:
        # All-day event
        return datetime.strptime(dt_info["date"], "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
    return datetime.now(timezone.utc)


def _parse_event(event: dict, calendar_name: str = "") -> CalendarEvent:
    """Parse a raw Google Calendar API event into a CalendarEvent."""
    # Extract attendees
    attendees = []
    for att in event.get("attendees", []):
        name = att.get("displayName", att.get("email", ""))
        if name:
            attendees.append(name)

    # Extract Google Meet link
    meet_link = ""
    conference = event.get("conferenceData", {})
    for ep in conference.get("entryPoints", []):
        if ep.get("entryPointType") == "video":
            meet_link = ep.get("uri", "")
            break

    # Organizer
    organizer_info = event.get("organizer", {})
    organizer = organizer_info.get("displayName", organizer_info.get("email", ""))

    return CalendarEvent(
        id=event.get("id", ""),
        summary=event.get("summary", "(No title)"),
        start=_parse_datetime(event.get("start", {})),
        end=_parse_datetime(event.get("end", {})),
        attendees=attendees,
        location=event.get("location", ""),
        meet_link=meet_link,
        description=event.get("description", ""),
        calendar_name=calendar_name,
        status=event.get("status", ""),
        organizer=organizer,
    )


def list_events(
    days: int = 1,
    date: str = "",
    limit: int = 50,
    calendar_id: str = "primary",
) -> list[CalendarEvent]:
    """List calendar events for a date range.

    Args:
        days: Number of days from today (default 1 = today only)
        date: Specific date in YYYY-MM-DD format (overrides days)
        limit: Max events to return
        calendar_id: Calendar ID (default: primary)
    """
    service = get_service()

    if date:
        start_dt = datetime.strptime(date, "%Y-%m-%d").replace(
            hour=0, minute=0, second=0, tzinfo=timezone.utc
        )
        end_dt = start_dt + timedelta(days=1)
    else:
        now = datetime.now(timezone.utc)
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(days=days)

    time_min = start_dt.isoformat()
    time_max = end_dt.isoformat()

    results = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = results.get("items", [])
    return [_parse_event(e, calendar_name=calendar_id) for e in events]


def get_upcoming(minutes: int = 30, calendar_id: str = "primary") -> list[CalendarEvent]:
    """Get events starting within the next N minutes."""
    service = get_service()

    now = datetime.now(timezone.utc)
    end_dt = now + timedelta(minutes=minutes)

    results = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now.isoformat(),
            timeMax=end_dt.isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = results.get("items", [])
    return [_parse_event(e) for e in events]


def format_event_list(events: list[CalendarEvent]) -> str:
    """Format event list for display."""
    if not events:
        return "No events found."

    lines = []
    current_date = None

    for e in events:
        event_date = e.start.strftime("%Y-%m-%d")
        if event_date != current_date:
            if current_date is not None:
                lines.append("")
            lines.append(f"--- {e.start.strftime('%A, %B %d %Y')} ---")
            current_date = event_date

        start_time = e.start.strftime("%H:%M")
        end_time = e.end.strftime("%H:%M")
        duration = e.end - e.start
        dur_min = int(duration.total_seconds() / 60)

        lines.append(f"  {start_time}-{end_time} ({dur_min}m)  {e.summary}")

        if e.attendees:
            attendee_str = ", ".join(e.attendees[:5])
            if len(e.attendees) > 5:
                attendee_str += f" +{len(e.attendees) - 5} more"
            lines.append(f"    Attendees: {attendee_str}")

        if e.location:
            lines.append(f"    Location: {e.location}")

        if e.meet_link:
            lines.append(f"    Meet: {e.meet_link}")

        if e.organizer:
            lines.append(f"    Organizer: {e.organizer}")

        lines.append("")

    return "\n".join(lines)


def format_event_detail(event: CalendarEvent) -> str:
    """Format a single event with full details."""
    lines = [
        f"Event: {event.summary}",
        f"When: {event.start.strftime('%Y-%m-%d %H:%M')} - {event.end.strftime('%H:%M')}",
    ]

    if event.organizer:
        lines.append(f"Organizer: {event.organizer}")
    if event.attendees:
        lines.append(f"Attendees: {', '.join(event.attendees)}")
    if event.location:
        lines.append(f"Location: {event.location}")
    if event.meet_link:
        lines.append(f"Meet Link: {event.meet_link}")
    if event.description:
        lines.append(f"\nDescription:\n{event.description}")

    return "\n".join(lines)
