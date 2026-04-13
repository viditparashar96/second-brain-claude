#!/bin/bash
#
# Second Brain — launchd Service Manager
#
# Usage:
#   ./launch_setup.sh install    # Install and start all services
#   ./launch_setup.sh uninstall  # Stop and remove all services
#   ./launch_setup.sh status     # Check which services are running
#   ./launch_setup.sh restart    # Restart all services
#   ./launch_setup.sh logs       # Show recent log output

set -e

PLIST_DIR="/Users/viditparashar/Desktop/second-brain-starter/.claude/launchd"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
LOG_DIR="/Users/viditparashar/Desktop/second-brain-starter/.claude/data/logs"

SERVICES=(
    "com.secondbrain.heartbeat"
    "com.secondbrain.reflect"
    "com.secondbrain.index"
    "com.secondbrain.slackbot"
)

install() {
    echo "Installing Second Brain services..."
    mkdir -p "$LAUNCH_AGENTS"
    mkdir -p "$LOG_DIR"

    for service in "${SERVICES[@]}"; do
        plist="$PLIST_DIR/$service.plist"
        dest="$LAUNCH_AGENTS/$service.plist"

        if [ ! -f "$plist" ]; then
            echo "  [!] Missing: $plist"
            continue
        fi

        # Unload if already loaded
        launchctl bootout "gui/$(id -u)/$service" 2>/dev/null || true

        # Copy and load
        cp "$plist" "$dest"
        launchctl bootstrap "gui/$(id -u)" "$dest"
        echo "  [+] Installed: $service"
    done

    echo ""
    echo "All services installed. Checking status..."
    status
}

uninstall() {
    echo "Uninstalling Second Brain services..."

    for service in "${SERVICES[@]}"; do
        dest="$LAUNCH_AGENTS/$service.plist"

        launchctl bootout "gui/$(id -u)/$service" 2>/dev/null || true

        if [ -f "$dest" ]; then
            rm "$dest"
            echo "  [-] Removed: $service"
        else
            echo "  [ ] Not installed: $service"
        fi
    done

    echo "All services removed."
}

status() {
    echo "Second Brain Service Status:"
    echo "───────────────────────────────────────────"

    for service in "${SERVICES[@]}"; do
        pid=$(launchctl print "gui/$(id -u)/$service" 2>/dev/null | grep "pid" | head -1 | awk '{print $3}')
        state=$(launchctl print "gui/$(id -u)/$service" 2>/dev/null | grep "state" | head -1 | awk '{print $3}')

        if [ -n "$state" ]; then
            short_name="${service#com.secondbrain.}"
            printf "  %-12s  state: %-10s  pid: %s\n" "$short_name" "$state" "${pid:-N/A}"
        else
            short_name="${service#com.secondbrain.}"
            printf "  %-12s  NOT LOADED\n" "$short_name"
        fi
    done

    echo "───────────────────────────────────────────"
}

restart() {
    echo "Restarting Second Brain services..."

    for service in "${SERVICES[@]}"; do
        launchctl kickstart -k "gui/$(id -u)/$service" 2>/dev/null || true
        echo "  [~] Restarted: $service"
    done

    sleep 2
    status
}

logs() {
    echo "Recent logs (last 5 lines each):"
    echo ""

    for logfile in "$LOG_DIR"/*-stdout.log; do
        if [ -f "$logfile" ]; then
            name=$(basename "$logfile" -stdout.log)
            echo "=== $name ==="
            tail -5 "$logfile" 2>/dev/null || echo "  (empty)"
            echo ""
        fi
    done

    # Check for errors
    echo "=== Recent Errors ==="
    for logfile in "$LOG_DIR"/*-stderr.log; do
        if [ -f "$logfile" ] && [ -s "$logfile" ]; then
            name=$(basename "$logfile" -stderr.log)
            echo "--- $name ---"
            tail -5 "$logfile" 2>/dev/null
            echo ""
        fi
    done
}

# Main
case "${1:-}" in
    install)
        install
        ;;
    uninstall)
        uninstall
        ;;
    status)
        status
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {install|uninstall|status|restart|logs}"
        exit 1
        ;;
esac
