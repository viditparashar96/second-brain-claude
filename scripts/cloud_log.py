"""Cloud Memory Logger — sends notes to the Cloud MCP server via HTTP.

Used by hooks (SessionEnd, Stop) to auto-log conversation outcomes
to the cloud vault instead of local files.

Config: reads CLOUD_MCP_URL and CLOUD_API_KEY from ~/.second-brain/config.json
or environment variables.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

# Config sources (env vars override config.json)
CLOUD_MCP_URL = os.environ.get("CLOUD_MCP_URL", "")
CLOUD_API_KEY = os.environ.get("CLOUD_API_KEY", "")

if not CLOUD_MCP_URL:
    # Try reading from config.json
    config_path = Path.home() / ".second-brain" / "config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            CLOUD_MCP_URL = config.get("cloud_mcp_url", "")
            CLOUD_API_KEY = config.get("cloud_api_key", "")
        except Exception:
            pass


def log_note(note: str) -> bool:
    """Send a note to the cloud MCP server's log_note tool. Returns True on success."""
    if not CLOUD_MCP_URL:
        return False

    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "log_note", "arguments": {"note": note}},
            "id": 1,
        }).encode()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if CLOUD_API_KEY:
            headers["Authorization"] = f"Bearer {CLOUD_API_KEY}"

        req = urllib.request.Request(CLOUD_MCP_URL, data=payload, headers=headers)
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status == 200
    except Exception as e:
        # Silent fail — don't break the hook if cloud is down
        print(f"Cloud log failed: {e}", file=sys.stderr)
        return False


def create_vault_file(file_path: str, content: str) -> bool:
    """Create/update a file in the cloud vault. Returns True on success."""
    if not CLOUD_MCP_URL:
        return False

    try:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "create_vault_file", "arguments": {"file_path": file_path, "content": content}},
            "id": 1,
        }).encode()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if CLOUD_API_KEY:
            headers["Authorization"] = f"Bearer {CLOUD_API_KEY}"

        req = urllib.request.Request(CLOUD_MCP_URL, data=payload, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status == 200
    except Exception as e:
        print(f"Cloud vault write failed: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # CLI usage: python cloud_log.py "note text here"
    if len(sys.argv) > 1:
        note = " ".join(sys.argv[1:])
        success = log_note(note)
        print(f"{'OK' if success else 'FAILED'}: {note}")
    else:
        print("Usage: python cloud_log.py <note>")
