#!/bin/bash
#
# Second Brain Plugin — Background Service Manager
#
# Usage:
#   ./launch_setup.sh install <plugin_root>   # Install and start all services
#   ./launch_setup.sh uninstall               # Stop and remove all services
#   ./launch_setup.sh status                  # Check which services are running
#   ./launch_setup.sh restart                 # Restart all services
#   ./launch_setup.sh logs                    # Show recent log output

set -e

SB_HOME="$HOME/.second-brain"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
LOG_DIR="$SB_HOME/data/logs"
VENV_PYTHON="$SB_HOME/.venv/bin/python3"

SERVICES=(
    "com.secondbrain.heartbeat"
    "com.secondbrain.reflect"
    "com.secondbrain.index"
)

# Detect plugin root from arg or current dir
PLUGIN_ROOT="${2:-$(cd "$(dirname "$0")/.." && pwd)}"

generate_plist() {
    local service="$1"
    local script="$2"
    local interval="$3"    # empty for calendar-based
    local calendar="$4"    # empty for interval-based
    local keep_alive="$5"  # "true" or empty

    cat <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${service}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${VENV_PYTHON}</string>
        <string>${PLUGIN_ROOT}/scripts/${script}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${SB_HOME}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>SECOND_BRAIN_HOME</key>
        <string>${SB_HOME}</string>
        <key>CLAUDE_PLUGIN_ROOT</key>
        <string>${PLUGIN_ROOT}</string>
    </dict>
PLIST

    if [ -n "$interval" ]; then
        cat <<PLIST
    <key>StartInterval</key>
    <integer>${interval}</integer>
PLIST
    fi

    if [ -n "$calendar" ]; then
        cat <<PLIST
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>${calendar}</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
PLIST
    fi

    if [ "$keep_alive" = "true" ]; then
        cat <<PLIST
    <key>KeepAlive</key>
    <true/>
PLIST
    fi

    cat <<PLIST
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/${service##*.}-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/${service##*.}-stderr.log</string>
</dict>
</plist>
PLIST
}

install() {
    echo "Installing Second Brain background services..."
    echo "Plugin root: $PLUGIN_ROOT"
    echo "Data dir: $SB_HOME"

    mkdir -p "$LAUNCH_AGENTS" "$LOG_DIR"

    # Check venv exists
    if [ ! -f "$VENV_PYTHON" ]; then
        echo "  Creating venv at $SB_HOME/.venv/..."
        python3 -m venv "$SB_HOME/.venv"
        "$VENV_PYTHON" -m pip install -q -r "$PLUGIN_ROOT/requirements.txt"
    fi

    # Heartbeat — every 30 min
    local dest="$LAUNCH_AGENTS/com.secondbrain.heartbeat.plist"
    launchctl bootout "gui/$(id -u)/com.secondbrain.heartbeat" 2>/dev/null || true
    generate_plist "com.secondbrain.heartbeat" "heartbeat.py" "1800" "" "" > "$dest"
    launchctl bootstrap "gui/$(id -u)" "$dest"
    echo "  [+] Heartbeat (every 30 min)"

    # Reflection — daily at 8am
    dest="$LAUNCH_AGENTS/com.secondbrain.reflect.plist"
    launchctl bootout "gui/$(id -u)/com.secondbrain.reflect" 2>/dev/null || true
    generate_plist "com.secondbrain.reflect" "memory_reflect.py" "" "8" "" > "$dest"
    launchctl bootstrap "gui/$(id -u)" "$dest"
    echo "  [+] Reflection (daily 8am)"

    # Index — every 15 min
    dest="$LAUNCH_AGENTS/com.secondbrain.index.plist"
    launchctl bootout "gui/$(id -u)/com.secondbrain.index" 2>/dev/null || true
    generate_plist "com.secondbrain.index" "memory_index.py" "900" "" "" > "$dest"
    launchctl bootstrap "gui/$(id -u)" "$dest"
    echo "  [+] Vault indexer (every 15 min)"

    echo ""
    echo "All services installed."
    status
}

uninstall() {
    echo "Removing Second Brain background services..."
    for service in "${SERVICES[@]}"; do
        launchctl bootout "gui/$(id -u)/$service" 2>/dev/null || true
        rm -f "$LAUNCH_AGENTS/$service.plist"
        echo "  [-] Removed: ${service##*.}"
    done
    echo "Done."
}

status() {
    echo "Second Brain Background Services:"
    echo "───────────────────────────────────────"
    for service in "${SERVICES[@]}"; do
        local short="${service##*.}"
        local state=$(launchctl print "gui/$(id -u)/$service" 2>/dev/null | grep "state" | head -1 | awk '{print $3}')
        if [ -n "$state" ]; then
            printf "  %-12s  %s\n" "$short" "$state"
        else
            printf "  %-12s  NOT LOADED\n" "$short"
        fi
    done
    echo "───────────────────────────────────────"
}

restart() {
    echo "Restarting..."
    for service in "${SERVICES[@]}"; do
        launchctl kickstart -k "gui/$(id -u)/$service" 2>/dev/null || true
        echo "  [~] ${service##*.}"
    done
    sleep 2
    status
}

logs() {
    echo "Recent logs:"
    echo ""
    for logfile in "$LOG_DIR"/*-stdout.log; do
        [ -f "$logfile" ] || continue
        local name=$(basename "$logfile" -stdout.log)
        echo "=== $name ==="
        tail -5 "$logfile" 2>/dev/null || echo "  (empty)"
        echo ""
    done
}

case "${1:-}" in
    install)   install ;;
    uninstall) uninstall ;;
    status)    status ;;
    restart)   restart ;;
    logs)      logs ;;
    *)
        echo "Usage: $0 {install|uninstall|status|restart|logs} [plugin_root]"
        exit 1
        ;;
esac
