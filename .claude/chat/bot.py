#!/usr/bin/env python3
"""
Second Brain Chat Bot — Slack bot entry point.

Connects to Slack via Socket Mode, handles DMs and @mentions,
maintains conversation context per thread, and can summarize
what happened in channels while you were away.

Usage:
    python bot.py

Environment variables required:
    SLACK_BOT_TOKEN   — Bot User OAuth Token (xoxb-...)
    SLACK_APP_TOKEN   — App-Level Token (xapp-...)
    ANTHROPIC_API_KEY — For Claude reasoning (optional but recommended)
"""

import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from threading import Event

# Add dirs to path
CHAT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = CHAT_DIR.parent / "scripts"
sys.path.insert(0, str(CHAT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(CHAT_DIR.parent.parent)
)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

from platform_adapter import IncomingMessage
from slack_adapter import SlackAdapter
from session_store import SessionStore

VAULT_DIR = Path(PROJECT_DIR) / "Dynamous" / "Memory"
LOG_FILE = Path(PROJECT_DIR) / ".claude" / "data" / "logs" / "chatbot.log"

IST = timezone(timedelta(hours=5, minutes=30))


def log(msg: str):
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass


# ─── Claude Reasoning ────────────────────────────────────────────

def get_claude_response(
    user_message: str,
    conversation_history: list[dict],
    extra_context: str = "",
) -> str:
    """Get a response from Claude with conversation history and vault context."""
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from claude_client import get_client, get_model_id

        client = get_client()
        if not client:
            return (
                "I can't reason right now — no Claude API keys configured in .env. "
                "Set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (Bedrock) or ANTHROPIC_API_KEY. "
                "I can still relay data from integrations. Try 'status' or 'what did I miss?'"
            )

        # Load SOUL.md for personality
        soul_path = VAULT_DIR / "SOUL.md"
        soul = soul_path.read_text() if soul_path.exists() else ""

        # Load MEMORY.md for context
        memory_path = VAULT_DIR / "MEMORY.md"
        memory = memory_path.read_text() if memory_path.exists() else ""

        system_prompt = f"""{soul[:2000]}

## Current Memory Context
{memory[:2000]}

{extra_context}

You are responding via Slack. Keep responses concise and conversational.
Use Slack formatting: *bold*, _italic_, `code`, ```code blocks```.
Do not use markdown headers (#) — they don't render in Slack.

You have live access to Vidit's integrations. When integration data is provided below, use it to answer directly — don't say you can't access it.
You can see: Gmail emails, GitHub PRs/issues, Asana tasks/deadlines, and memory vault search results."""

        # Build messages array
        messages = []
        for msg in conversation_history[-20:]:  # Last 20 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        response = client.messages.create(
            model=get_model_id(),
            max_tokens=1000,
            system=system_prompt,
            messages=messages,
        )

        return response.content[0].text

    except Exception as e:
        log(f"Claude response failed: {e}")
        return f"Something went wrong: {e}"


# ─── Summarize Channel ───────────────────────────────────────────

def summarize_channel(adapter: SlackAdapter, channel_id: str, hours: int = 8) -> str:
    """Fetch recent channel messages and summarize with Claude."""
    # Calculate oldest timestamp (N hours ago)
    oldest_dt = datetime.now() - timedelta(hours=hours)
    oldest_ts = str(oldest_dt.timestamp())

    messages = adapter.get_channel_history(channel_id, limit=200, oldest=oldest_ts)

    if not messages:
        return "No messages found in that time period."

    # Format messages for Claude
    formatted = []
    for msg in reversed(messages):  # Chronological order
        formatted.append(f"{msg['user']}: {msg['text']}")

    context = "\n".join(formatted)

    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from claude_client import create_message

        result = create_message(
            system="Summarize this Slack conversation concisely. Group by topic. Highlight decisions, action items, and anything that needs attention. Use Slack formatting.",
            messages=[{
                "role": "user",
                "content": f"Summarize the last {hours} hours of this channel:\n\n{context[:8000]}"
            }],
            max_tokens=800,
        )

        if not result:
            return f"Found {len(messages)} messages but no Claude API keys configured in .env."

        return result

    except Exception as e:
        log(f"Summarization failed: {e}")
        return f"Summarization failed: {e}"


# ─── Quick Status ────────────────────────────────────────────────

def get_quick_status() -> str:
    """Generate a quick status from the heartbeat state."""
    state_path = Path(PROJECT_DIR) / ".claude" / "data" / "state" / "heartbeat-state.json"

    if not state_path.exists():
        return "No heartbeat data yet. Run the heartbeat first: `python .claude/scripts/heartbeat.py --force`"

    import json
    state = json.loads(state_path.read_text())

    gmail = state.get("gmail", {})
    asana = state.get("asana", {})
    github = state.get("github", {})
    timestamp = state.get("timestamp", "unknown")

    lines = [f"*Status as of {timestamp}*\n"]

    # Gmail
    unread = gmail.get("unread_count", "?")
    lines.append(f"*Gmail:* {unread} unread")

    # Asana
    overdue = asana.get("overdue_count", 0)
    upcoming = asana.get("upcoming_count", 0)
    if overdue:
        tasks = asana.get("overdue_tasks", [])
        task_names = ", ".join(t["name"] for t in tasks[:3])
        lines.append(f"*Asana:* {overdue} overdue ({task_names}), {upcoming} upcoming")
    else:
        lines.append(f"*Asana:* No overdue tasks, {upcoming} upcoming")

    # GitHub
    remaining = github.get("rate_limit_remaining", "?")
    lines.append(f"*GitHub:* API rate limit {remaining} remaining")

    return "\n".join(lines)


# ─── Daily Log for Chat ──────────────────────────────────────────

def append_chat_to_daily(user_name: str, user_msg: str, bot_response: str):
    """Log bot conversations to the daily vault file."""
    DAILY_DIR = VAULT_DIR / "daily"
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(IST).strftime("%Y-%m-%d")
    log_path = DAILY_DIR / f"{today}.md"
    now = datetime.now(IST).strftime("%H:%M")

    # Truncate long messages for the log
    user_short = user_msg[:150] + "..." if len(user_msg) > 150 else user_msg
    bot_short = bot_response[:200] + "..." if len(bot_response) > 200 else bot_response

    entry = f"- **{now}** — [chat] {user_name}: {user_short}\n  - Bot: {bot_short}\n"

    try:
        if log_path.exists():
            content = log_path.read_text()
            if not content.endswith("\n"):
                entry = "\n" + entry
        else:
            entry = f"# Daily Log — {today}\n\n## Log\n\n" + entry

        with open(log_path, "a") as f:
            f.write(entry)
    except Exception as e:
        log(f"Failed to log chat to daily: {e}")


# ─── Integration Data Fetcher ─────────────────────────────────────

def fetch_integration_context(text_lower: str) -> str:
    """Detect if the user is asking about something an integration can answer,
    fetch the data, and return it as extra context for Claude."""
    import subprocess

    venv_python = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
    query_py = os.path.join(PROJECT_DIR, ".claude", "scripts", "integrations", "query.py")
    context_parts = []

    def run_query(*args) -> str:
        try:
            result = subprocess.run(
                [venv_python, query_py, *args],
                capture_output=True, text=True, timeout=30,
                cwd=PROJECT_DIR,
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    # Email related
    if any(kw in text_lower for kw in ["email", "mail", "inbox", "unread", "gmail"]):
        data = run_query("gmail", "list", "--limit", "5", "--unread")
        if not data:
            data = run_query("gmail", "list", "--limit", "5")
        if data:
            context_parts.append(f"## Recent Gmail Emails\n{data}")

    # GitHub related
    if any(kw in text_lower for kw in ["pr", "pull request", "issue", "github", "code review"]):
        data = run_query("github", "rate-limit")
        if data:
            context_parts.append(f"## GitHub Status\n{data}")

    # Asana/tasks/deadlines related
    if any(kw in text_lower for kw in ["task", "deadline", "overdue", "asana", "assana", "due", "todo", "check"]):
        overdue = run_query("asana", "overdue")
        upcoming = run_query("asana", "upcoming", "--days", "7")
        if overdue:
            context_parts.append(f"## Overdue Tasks\n{overdue}")
        if upcoming:
            context_parts.append(f"## Upcoming Deadlines\n{upcoming}")

    # Memory search
    if any(kw in text_lower for kw in ["remember", "memory", "vault", "search", "find"]):
        search_py = os.path.join(PROJECT_DIR, ".claude", "scripts", "memory_search.py")
        try:
            result = subprocess.run(
                [venv_python, search_py, text_lower, "--top-k", "3"],
                capture_output=True, text=True, timeout=15,
                cwd=PROJECT_DIR,
            )
            if result.returncode == 0 and result.stdout.strip():
                context_parts.append(f"## Memory Search Results\n{result.stdout.strip()}")
        except Exception:
            pass

    if context_parts:
        return "\n\n".join(context_parts)
    return ""


# ─── Message Handler ─────────────────────────────────────────────

def create_message_handler(adapter: SlackAdapter, store: SessionStore):
    """Create the main message handler function."""

    def handle_message(msg: IncomingMessage):
        log(f"Message from {msg.user_name} in {msg.channel_id}: {msg.text[:100]}")

        text_lower = msg.text.lower().strip()

        # Quick commands (no LLM needed)
        if text_lower in ("status", "status?"):
            adapter.send_message(msg.channel_id, get_quick_status(), msg.thread_id)
            return

        if text_lower in ("what did i miss", "what did i miss?", "catch me up", "summary"):
            adapter.send_message(
                msg.channel_id,
                "Summarizing the last 8 hours...",
                msg.thread_id,
            )
            summary = summarize_channel(adapter, msg.channel_id, hours=8)
            adapter.send_message(msg.channel_id, summary, msg.thread_id)
            return

        if text_lower.startswith("summarize last "):
            try:
                hours = int(text_lower.split("summarize last ")[1].split("h")[0].strip())
            except ValueError:
                hours = 8
            adapter.send_message(
                msg.channel_id,
                f"Summarizing the last {hours} hours...",
                msg.thread_id,
            )
            summary = summarize_channel(adapter, msg.channel_id, hours=hours)
            adapter.send_message(msg.channel_id, summary, msg.thread_id)
            return

        if text_lower in ("clear", "reset", "new conversation"):
            store.clear_session(msg.thread_id)
            adapter.send_message(msg.channel_id, "Conversation cleared.", msg.thread_id)
            return

        if text_lower in ("help", "help?"):
            help_text = (
                "*Second Brain Bot Commands:*\n"
                "- `status` — Quick overview from last heartbeat\n"
                "- `what did I miss?` — Summarize recent channel activity\n"
                "- `summarize last Nh` — Summarize last N hours\n"
                "- `clear` — Reset conversation in this thread\n"
                "- `help` — Show this message\n"
                "- _Anything else_ — Chat with your Second Brain"
            )
            adapter.send_message(msg.channel_id, help_text, msg.thread_id)
            return

        # Full Claude conversation
        try:
            history = store.get_messages(msg.thread_id)

            # Fetch integration data if the message is about email/tasks/PRs/etc.
            extra_context = fetch_integration_context(text_lower)

            # Store user message
            store.add_message(msg.thread_id, msg.channel_id, "user", msg.text)

            # Get Claude response (with integration data as extra context)
            response = get_claude_response(msg.text, history, extra_context=extra_context)

            # Store assistant response
            store.add_message(msg.thread_id, msg.channel_id, "assistant", response)

            # Send to Slack
            adapter.send_message(msg.channel_id, response, msg.thread_id)

            # Log to daily vault (persistent memory)
            append_chat_to_daily(msg.user_name, msg.text, response)
        except Exception as e:
            log(f"Message handling error: {e}")
            adapter.send_message(msg.channel_id, f"Error: {e}", msg.thread_id)

    return handle_message


# ─── Main ────────────────────────────────────────────────────────

def main():
    print("Starting Second Brain Slack Bot...")
    log("Bot starting")

    adapter = SlackAdapter()
    store = SessionStore()

    handler = create_message_handler(adapter, store)
    adapter.on_message(handler)

    adapter.connect()

    print("Bot is running. Press Ctrl+C to stop.")
    log("Bot connected and listening")

    try:
        Event().wait()  # Block forever until interrupted
    except KeyboardInterrupt:
        print("\nShutting down...")
        log("Bot shutting down")
        adapter.disconnect()
        store.close()


if __name__ == "__main__":
    main()
