"""
Slack Adapter — Socket Mode implementation of PlatformAdapter.

Uses slack_sdk Socket Mode (outbound WebSocket, no public URL needed).
Handles message.im, app_mention events. Posts responses in threads.
"""

import os
import sys
from pathlib import Path
from typing import Callable

from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.errors import SlackApiError

from platform_adapter import IncomingMessage

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent)
)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))


class SlackAdapter:
    """Slack Socket Mode adapter for the Second Brain chat bot."""

    def __init__(self):
        bot_token = os.environ.get("SLACK_BOT_TOKEN", "")
        app_token = os.environ.get("SLACK_APP_TOKEN", "")

        if not bot_token or not app_token:
            raise ValueError(
                "SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in .env. "
                "See Phase 7 setup instructions."
            )

        self.web_client = WebClient(token=bot_token)
        self.socket_client = SocketModeClient(
            app_token=app_token,
            web_client=self.web_client,
        )

        self._message_handler: Callable[[IncomingMessage], None] | None = None
        self._user_cache: dict[str, str] = {}
        self._bot_user_id: str = ""

    def connect(self):
        """Connect to Slack via Socket Mode and start listening."""
        # Get bot's own user ID to ignore self-messages
        try:
            auth = self.web_client.auth_test()
            self._bot_user_id = auth["user_id"]
        except SlackApiError as e:
            print(f"Auth test failed: {e}", file=sys.stderr)

        self.socket_client.socket_mode_request_listeners.append(self._handle_event)
        self.socket_client.connect()
        print(f"Slack bot connected (bot user: {self._bot_user_id})")

    def disconnect(self):
        """Disconnect from Slack."""
        self.socket_client.disconnect()
        print("Slack bot disconnected")

    def on_message(self, handler: Callable[[IncomingMessage], None]):
        """Register the message handler."""
        self._message_handler = handler

    def send_message(self, channel_id: str, text: str, thread_id: str = ""):
        """Send a message to a Slack channel/DM, optionally in a thread."""
        try:
            kwargs = {"channel": channel_id, "text": text}
            if thread_id:
                kwargs["thread_ts"] = thread_id
            self.web_client.chat_postMessage(**kwargs)
        except SlackApiError as e:
            print(f"Failed to send message: {e}", file=sys.stderr)

    def get_channel_history(
        self, channel_id: str, limit: int = 100, oldest: str = ""
    ) -> list[dict]:
        """Fetch recent messages from a channel for summarization."""
        try:
            kwargs = {"channel": channel_id, "limit": min(limit, 200)}
            if oldest:
                kwargs["oldest"] = oldest

            result = self.web_client.conversations_history(**kwargs)
            messages = result.get("messages", [])

            # Resolve user names
            formatted = []
            for msg in messages:
                user_id = msg.get("user", "")
                user_name = self.resolve_user(user_id) if user_id else "unknown"
                formatted.append({
                    "user": user_name,
                    "text": msg.get("text", ""),
                    "ts": msg.get("ts", ""),
                })

            return formatted

        except SlackApiError as e:
            print(f"Failed to fetch history: {e}", file=sys.stderr)
            return []

    def resolve_user(self, user_id: str) -> str:
        """Resolve a Slack user ID to a display name (cached)."""
        if user_id in self._user_cache:
            return self._user_cache[user_id]

        try:
            result = self.web_client.users_info(user=user_id)
            user = result.get("user", {})
            name = (
                user.get("real_name")
                or user.get("profile", {}).get("display_name")
                or user.get("name", user_id)
            )
            self._user_cache[user_id] = name
            return name
        except SlackApiError:
            return user_id

    def _handle_event(self, client: SocketModeClient, req: SocketModeRequest):
        """Handle incoming Socket Mode events."""
        # Always acknowledge immediately
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        if req.type != "events_api":
            return

        event = req.payload.get("event", {})
        event_type = event.get("type", "")

        # Ignore bot's own messages
        if event.get("user") == self._bot_user_id:
            return
        if event.get("bot_id"):
            return

        # Handle relevant event types
        if event_type == "message" and not event.get("subtype"):
            self._handle_message_event(event)
        elif event_type == "app_mention":
            self._handle_message_event(event, is_mention=True)

    def _handle_message_event(self, event: dict, is_mention: bool = False):
        """Process a message event and dispatch to the handler."""
        if not self._message_handler:
            return

        text = event.get("text", "").strip()
        if not text:
            return

        # Strip bot mention from text if present
        if self._bot_user_id and f"<@{self._bot_user_id}>" in text:
            text = text.replace(f"<@{self._bot_user_id}>", "").strip()

        channel_id = event.get("channel", "")
        user_id = event.get("user", "")
        thread_ts = event.get("thread_ts", event.get("ts", ""))
        channel_type = event.get("channel_type", "")

        is_dm = channel_type == "im"

        user_name = self.resolve_user(user_id) if user_id else ""

        msg = IncomingMessage(
            text=text,
            channel_id=channel_id,
            thread_id=thread_ts,
            user_id=user_id,
            user_name=user_name,
            is_dm=is_dm,
            is_mention=is_mention,
        )

        self._message_handler(msg)
