"""
Session Store — SQLite-backed conversation persistence for the chat bot.

Maps Slack thread_ts → conversation history so each thread maintains
multi-turn context. Sessions survive bot restarts.

Thread-safe: creates a new connection per call since Socket Mode
dispatches handlers on different threads.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chat.db"


class SessionStore:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = str(Path(db_path) if db_path else DEFAULT_DB_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        # Create schema on init
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    thread_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    messages TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        """Create a new connection (thread-safe)."""
        return sqlite3.connect(self.db_path)

    def get_messages(self, thread_id: str) -> list[dict]:
        """Get conversation history for a thread."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT messages FROM sessions WHERE thread_id = ?",
                (thread_id,)
            ).fetchone()
        if row:
            return json.loads(row[0])
        return []

    def add_message(self, thread_id: str, channel_id: str, role: str, content: str):
        """Add a message to a thread's conversation history."""
        now = datetime.now().isoformat()
        messages = self.get_messages(thread_id)
        messages.append({"role": role, "content": content})

        # Keep last 50 messages per thread to avoid unbounded growth
        if len(messages) > 50:
            messages = messages[-50:]

        messages_json = json.dumps(messages)

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO sessions (thread_id, channel_id, messages, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    messages = excluded.messages,
                    updated_at = excluded.updated_at
            """, (thread_id, channel_id, messages_json, now, now))
            conn.commit()

    def clear_session(self, thread_id: str):
        """Clear a thread's conversation history."""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM sessions WHERE thread_id = ?",
                (thread_id,)
            )
            conn.commit()

    def get_active_sessions(self, limit: int = 20) -> list[dict]:
        """List recent active sessions."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT thread_id, channel_id, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [
            {"thread_id": r[0], "channel_id": r[1], "updated_at": r[2]}
            for r in rows
        ]

    def close(self):
        pass  # No persistent connection to close
