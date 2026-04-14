#!/usr/bin/env bash
# Second Brain MCP Server Launcher
# Finds the correct Python (venv > system), ensures deps, starts the server.
# Used by both .mcp.json (Claude Code) and claude_desktop_config.json (Claude Desktop).

set -euo pipefail

SECOND_BRAIN_HOME="${SECOND_BRAIN_HOME:-$HOME/.second-brain}"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
VENV_DIR="$SECOND_BRAIN_HOME/.venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
SERVER="$PLUGIN_ROOT/mcp-server/server.py"
LOG_FILE="$SECOND_BRAIN_HOME/data/logs/mcp-server.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log "=== MCP Server starting ==="
log "PLUGIN_ROOT=$PLUGIN_ROOT"
log "SECOND_BRAIN_HOME=$SECOND_BRAIN_HOME"

# Step 1: Find Python
if [ -x "$VENV_PYTHON" ]; then
    PYTHON="$VENV_PYTHON"
    log "Using venv Python: $PYTHON"
else
    log "Venv not found at $VENV_PYTHON — creating..."

    # Find system python
    PYTHON=""
    for candidate in python3 python; do
        if command -v "$candidate" &>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    done

    if [ -z "$PYTHON" ]; then
        log "ERROR: No python3 found on PATH"
        echo "Error: Python 3 not found. Install Python 3.10+ first." >&2
        exit 1
    fi

    log "Using system Python: $PYTHON (version: $($PYTHON --version 2>&1))"

    # Create venv
    mkdir -p "$SECOND_BRAIN_HOME"
    if $PYTHON -m venv "$VENV_DIR" >> "$LOG_FILE" 2>&1; then
        log "Venv created at $VENV_DIR"
        PYTHON="$VENV_PYTHON"
    else
        log "WARNING: Venv creation failed, using system Python"
    fi

    # Install requirements
    if [ -x "$VENV_PYTHON" ] && [ -f "$PLUGIN_ROOT/requirements.txt" ]; then
        log "Installing dependencies..."
        if "$VENV_PYTHON" -m pip install -q -r "$PLUGIN_ROOT/requirements.txt" >> "$LOG_FILE" 2>&1; then
            log "Dependencies installed successfully"
            PYTHON="$VENV_PYTHON"
        else
            log "WARNING: pip install failed — some features may not work"
        fi
    fi
fi

# Step 2: Verify mcp package is importable
if ! "$PYTHON" -c "import mcp" 2>/dev/null; then
    log "ERROR: mcp package not importable. Installing..."
    "$PYTHON" -m pip install -q mcp >> "$LOG_FILE" 2>&1 || {
        log "FATAL: Could not install mcp package"
        echo "Error: Could not install MCP package. Check $LOG_FILE for details." >&2
        exit 1
    }
fi

# Step 3: Export env and launch server
export SECOND_BRAIN_HOME
export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"

log "Launching server: $PYTHON $SERVER"
exec "$PYTHON" "$SERVER" 2>> "$LOG_FILE"
