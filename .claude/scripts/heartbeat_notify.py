"""
macOS Notification Helper — Send native notifications via osascript.

Usage:
    from heartbeat_notify import notify
    notify("Second Brain", "You have 3 overdue Asana tasks")
"""

import subprocess
import sys


def notify(title: str, message: str, subtitle: str = "", sound: str = "default"):
    """Send a macOS native notification via osascript."""
    # Escape double quotes for AppleScript
    title = title.replace('"', '\\"')
    message = message.replace('"', '\\"')
    subtitle = subtitle.replace('"', '\\"')

    script = f'display notification "{message}" with title "{title}"'
    if subtitle:
        script += f' subtitle "{subtitle}"'
    if sound:
        script += f' sound name "{sound}"'

    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, timeout=5
        )
    except Exception as e:
        print(f"Notification failed: {e}", file=sys.stderr)


def notify_urgent(items: list[str]):
    """Send a notification for urgent items (batched into one notification)."""
    if not items:
        return

    count = len(items)
    if count == 1:
        notify("Second Brain", items[0], subtitle="Needs attention")
    else:
        summary = f"{count} items need attention"
        body = "\n".join(f"- {item}" for item in items[:5])
        if count > 5:
            body += f"\n... and {count - 5} more"
        notify("Second Brain", body, subtitle=summary)


if __name__ == "__main__":
    # Quick test
    notify("Second Brain", "Heartbeat notification test", subtitle="Phase 6")
    print("Notification sent (check your macOS notification center)")
