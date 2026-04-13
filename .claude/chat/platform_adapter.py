"""
Platform Adapter Protocol — Abstract interface for chat platforms.

Defines the contract that any chat platform (Slack, Discord, Teams)
must implement to work with the bot. SlackAdapter is the first implementation.
"""

from typing import Protocol, Callable


class IncomingMessage:
    """A message received from a chat platform."""

    def __init__(
        self,
        text: str,
        channel_id: str,
        thread_id: str,
        user_id: str,
        user_name: str = "",
        is_dm: bool = False,
        is_mention: bool = False,
    ):
        self.text = text
        self.channel_id = channel_id
        self.thread_id = thread_id  # thread_ts for Slack
        self.user_id = user_id
        self.user_name = user_name
        self.is_dm = is_dm
        self.is_mention = is_mention


class PlatformAdapter(Protocol):
    """Protocol that chat platform adapters must implement."""

    def connect(self) -> None:
        """Establish connection to the platform."""
        ...

    def disconnect(self) -> None:
        """Disconnect from the platform."""
        ...

    def send_message(self, channel_id: str, text: str, thread_id: str = "") -> None:
        """Send a message to a channel, optionally in a thread."""
        ...

    def on_message(self, handler: Callable[[IncomingMessage], None]) -> None:
        """Register a handler for incoming messages."""
        ...

    def get_channel_history(
        self, channel_id: str, limit: int = 100, oldest: str = ""
    ) -> list[dict]:
        """Fetch recent messages from a channel (for summarization)."""
        ...

    def resolve_user(self, user_id: str) -> str:
        """Resolve a user ID to a display name."""
        ...
