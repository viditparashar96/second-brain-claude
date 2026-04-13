#!/usr/bin/env python3
"""
Setup Second Brain MCP Server for Claude Desktop.

Adds the MCP server config to Claude Desktop's config file.
Run this once after plugin setup to enable Second Brain in Claude Desktop.

Usage:
    python setup_desktop.py [--uninstall]
"""

import json
import os
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import SECOND_BRAIN_HOME, PLUGIN_ROOT


def get_desktop_config_path() -> Path:
    """Get Claude Desktop config path based on OS."""
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    else:
        print(f"Unsupported OS: {system}")
        sys.exit(1)


def get_venv_python() -> str:
    """Get the venv python path."""
    venv = SECOND_BRAIN_HOME / ".venv" / "bin" / "python3"
    if venv.exists():
        return str(venv)
    return sys.executable


def install():
    config_path = get_desktop_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new
    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
        except Exception:
            config = {}

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add Second Brain MCP server
    server_path = str(PLUGIN_ROOT / "mcp-server" / "server.py")
    python_path = get_venv_python()

    config["mcpServers"]["second-brain"] = {
        "command": python_path,
        "args": [server_path],
        "env": {
            "SECOND_BRAIN_HOME": str(SECOND_BRAIN_HOME),
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT),
        }
    }

    config_path.write_text(json.dumps(config, indent=2))

    print("Second Brain MCP Server configured for Claude Desktop!")
    print(f"  Config: {config_path}")
    print(f"  Server: {server_path}")
    print(f"  Python: {python_path}")
    print()
    print("What's available in Claude Desktop:")
    print("  Resources: SOUL.md, USER.md, MEMORY.md, HABITS.md, today's log")
    print("             (auto-loaded into every conversation)")
    print("  Prompts:   status check, draft email, review PR, meeting notes,")
    print("             catch me up, search knowledge")
    print("  Tools:     16 tools — search, email, tasks, PRs, vault management")
    print()
    print("Restart Claude Desktop to connect.")


def uninstall():
    config_path = get_desktop_config_path()
    if not config_path.exists():
        print("Claude Desktop config not found.")
        return

    config = json.loads(config_path.read_text())
    if "mcpServers" in config and "second-brain" in config["mcpServers"]:
        del config["mcpServers"]["second-brain"]
        config_path.write_text(json.dumps(config, indent=2))
        print("Second Brain removed from Claude Desktop. Restart to apply.")
    else:
        print("Second Brain not found in Claude Desktop config.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
