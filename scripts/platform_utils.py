"""
Cross-platform utilities — OS detection, notifications, background services.

Supports macOS, Windows, and Linux.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SYSTEM = platform.system()  # "Darwin", "Windows", "Linux"


def get_os_name() -> str:
    """Human-readable OS name."""
    return {"Darwin": "macOS", "Windows": "Windows", "Linux": "Linux"}.get(SYSTEM, SYSTEM)


def check_python_version() -> tuple[bool, str]:
    """Check if Python 3.10+ is available. Returns (ok, message)."""
    v = sys.version_info
    if v.major == 3 and v.minor >= 10:
        return True, f"Python {v.major}.{v.minor}.{v.micro}"
    return False, f"Python {v.major}.{v.minor}.{v.micro} — need 3.10+"


def find_python() -> str | None:
    """Find a suitable Python 3.10+ executable."""
    for name in ["python3", "python", "python3.14", "python3.13", "python3.12", "python3.11", "python3.10"]:
        path = shutil.which(name)
        if path:
            try:
                result = subprocess.run(
                    [path, "-c", "import sys; print(sys.version_info.minor)"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0 and int(result.stdout.strip()) >= 10:
                    return path
            except Exception:
                continue
    return None


def notify(title: str, message: str):
    """Send an OS-native notification."""
    try:
        if SYSTEM == "Darwin":
            message = message.replace('"', '\\"')
            title = title.replace('"', '\\"')
            subprocess.run(
                ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
                capture_output=True, timeout=5,
            )
        elif SYSTEM == "Linux":
            subprocess.run(
                ["notify-send", title, message],
                capture_output=True, timeout=5,
            )
        elif SYSTEM == "Windows":
            # PowerShell toast notification
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $template.GetElementsByTagName('text')[0].AppendChild($template.CreateTextNode('{title}')) | Out-Null
            $template.GetElementsByTagName('text')[1].AppendChild($template.CreateTextNode('{message}')) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Second Brain').Show($toast)
            """
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True, timeout=5,
            )
    except Exception:
        pass


# ─── Background Service Management ──────────────────────────────

def install_background_services(plugin_root: str, sb_home: str, venv_python: str):
    """Install background services based on OS."""
    if SYSTEM == "Darwin":
        return _install_launchd(plugin_root, sb_home, venv_python)
    elif SYSTEM == "Linux":
        return _install_systemd(plugin_root, sb_home, venv_python)
    elif SYSTEM == "Windows":
        return _install_task_scheduler(plugin_root, sb_home, venv_python)
    return "Unsupported OS for background services"


def uninstall_background_services():
    """Remove background services based on OS."""
    if SYSTEM == "Darwin":
        return _uninstall_launchd()
    elif SYSTEM == "Linux":
        return _uninstall_systemd()
    elif SYSTEM == "Windows":
        return _uninstall_task_scheduler()
    return "Unsupported OS"


def get_service_status() -> str:
    """Get status of background services."""
    if SYSTEM == "Darwin":
        return _status_launchd()
    elif SYSTEM == "Linux":
        return _status_systemd()
    elif SYSTEM == "Windows":
        return _status_task_scheduler()
    return "Unsupported OS"


# ─── macOS (launchd) ────────────────────────────────────────────

LAUNCHD_SERVICES = [
    ("com.secondbrain.heartbeat", "heartbeat.py", 1800),
    ("com.secondbrain.index", "memory_index.py", 900),
]
LAUNCHD_CALENDAR_SERVICES = [
    ("com.secondbrain.reflect", "memory_reflect.py", 8),  # 8am
]


def _make_plist(label, script, plugin_root, sb_home, venv_python, interval=None, hour=None):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        '<dict>',
        f'    <key>Label</key><string>{label}</string>',
        '    <key>ProgramArguments</key><array>',
        f'        <string>{venv_python}</string>',
        f'        <string>{plugin_root}/scripts/{script}</string>',
        '    </array>',
        f'    <key>WorkingDirectory</key><string>{sb_home}</string>',
        '    <key>EnvironmentVariables</key><dict>',
        f'        <key>SECOND_BRAIN_HOME</key><string>{sb_home}</string>',
        f'        <key>CLAUDE_PLUGIN_ROOT</key><string>{plugin_root}</string>',
        '    </dict>',
    ]
    if interval:
        lines.append(f'    <key>StartInterval</key><integer>{interval}</integer>')
    if hour is not None:
        lines.extend([
            '    <key>StartCalendarInterval</key><dict>',
            f'        <key>Hour</key><integer>{hour}</integer>',
            '        <key>Minute</key><integer>0</integer>',
            '    </dict>',
        ])
    log_dir = f"{sb_home}/data/logs"
    short = label.split(".")[-1]
    lines.extend([
        '    <key>RunAtLoad</key><true/>',
        f'    <key>StandardOutPath</key><string>{log_dir}/{short}-stdout.log</string>',
        f'    <key>StandardErrorPath</key><string>{log_dir}/{short}-stderr.log</string>',
        '</dict>',
        '</plist>',
    ])
    return "\n".join(lines)


def _install_launchd(plugin_root, sb_home, venv_python):
    launch_dir = Path.home() / "Library" / "LaunchAgents"
    launch_dir.mkdir(parents=True, exist_ok=True)
    Path(f"{sb_home}/data/logs").mkdir(parents=True, exist_ok=True)
    uid = os.getuid()

    results = []
    for label, script, interval in LAUNCHD_SERVICES:
        plist = _make_plist(label, script, plugin_root, sb_home, venv_python, interval=interval)
        dest = launch_dir / f"{label}.plist"
        subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], capture_output=True)
        dest.write_text(plist)
        subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(dest)], capture_output=True)
        results.append(f"  [+] {label.split('.')[-1]}")

    for label, script, hour in LAUNCHD_CALENDAR_SERVICES:
        plist = _make_plist(label, script, plugin_root, sb_home, venv_python, hour=hour)
        dest = launch_dir / f"{label}.plist"
        subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], capture_output=True)
        dest.write_text(plist)
        subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(dest)], capture_output=True)
        results.append(f"  [+] {label.split('.')[-1]}")

    return "\n".join(results)


def _uninstall_launchd():
    uid = os.getuid()
    launch_dir = Path.home() / "Library" / "LaunchAgents"
    results = []
    for label, _, _ in LAUNCHD_SERVICES + LAUNCHD_CALENDAR_SERVICES:
        subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], capture_output=True)
        plist = launch_dir / f"{label}.plist"
        if plist.exists():
            plist.unlink()
        results.append(f"  [-] {label.split('.')[-1]}")
    return "\n".join(results)


def _status_launchd():
    uid = os.getuid()
    lines = []
    for label, _, _ in LAUNCHD_SERVICES + LAUNCHD_CALENDAR_SERVICES:
        short = label.split(".")[-1]
        try:
            result = subprocess.run(
                ["launchctl", "print", f"gui/{uid}/{label}"],
                capture_output=True, text=True,
            )
            state = "loaded" if result.returncode == 0 else "not loaded"
        except Exception:
            state = "unknown"
        lines.append(f"  {short:<12} {state}")
    return "\n".join(lines)


# ─── Windows (Task Scheduler) ───────────────────────────────────

def _install_task_scheduler(plugin_root, sb_home, venv_python):
    results = []
    for label, script, interval in LAUNCHD_SERVICES:
        short = label.split(".")[-1]
        minutes = interval // 60
        cmd = (
            f'schtasks /Create /TN "SecondBrain\\{short}" /TR '
            f'"\"{venv_python}\" \"{plugin_root}\\scripts\\{script}\"" '
            f'/SC MINUTE /MO {minutes} /F'
        )
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
            results.append(f"  [+] {short} (every {minutes}min)")
        except Exception as e:
            results.append(f"  [!] {short} failed: {e}")

    for label, script, hour in LAUNCHD_CALENDAR_SERVICES:
        short = label.split(".")[-1]
        cmd = (
            f'schtasks /Create /TN "SecondBrain\\{short}" /TR '
            f'"\"{venv_python}\" \"{plugin_root}\\scripts\\{script}\"" '
            f'/SC DAILY /ST {hour:02d}:00 /F'
        )
        try:
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
            results.append(f"  [+] {short} (daily {hour}:00)")
        except Exception as e:
            results.append(f"  [!] {short} failed: {e}")

    return "\n".join(results)


def _uninstall_task_scheduler():
    results = []
    for label, _, _ in LAUNCHD_SERVICES + LAUNCHD_CALENDAR_SERVICES:
        short = label.split(".")[-1]
        try:
            subprocess.run(
                f'schtasks /Delete /TN "SecondBrain\\{short}" /F',
                shell=True, capture_output=True,
            )
            results.append(f"  [-] {short}")
        except Exception:
            results.append(f"  [ ] {short} (not found)")
    return "\n".join(results)


def _status_task_scheduler():
    lines = []
    for label, _, _ in LAUNCHD_SERVICES + LAUNCHD_CALENDAR_SERVICES:
        short = label.split(".")[-1]
        try:
            result = subprocess.run(
                f'schtasks /Query /TN "SecondBrain\\{short}" /FO LIST',
                shell=True, capture_output=True, text=True,
            )
            state = "scheduled" if result.returncode == 0 else "not found"
        except Exception:
            state = "unknown"
        lines.append(f"  {short:<12} {state}")
    return "\n".join(lines)


# ─── Linux (systemd user services) ──────────────────────────────

def _install_systemd(plugin_root, sb_home, venv_python):
    unit_dir = Path.home() / ".config" / "systemd" / "user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    Path(f"{sb_home}/data/logs").mkdir(parents=True, exist_ok=True)
    results = []

    for label, script, interval in LAUNCHD_SERVICES:
        short = label.split(".")[-1]
        service = f"""[Unit]
Description=Second Brain {short}

[Service]
ExecStart={venv_python} {plugin_root}/scripts/{script}
Environment=SECOND_BRAIN_HOME={sb_home}
Environment=CLAUDE_PLUGIN_ROOT={plugin_root}
WorkingDirectory={sb_home}
"""
        timer = f"""[Unit]
Description=Second Brain {short} timer

[Timer]
OnBootSec=60
OnUnitActiveSec={interval}s

[Install]
WantedBy=timers.target
"""
        (unit_dir / f"secondbrain-{short}.service").write_text(service)
        (unit_dir / f"secondbrain-{short}.timer").write_text(timer)
        subprocess.run(["systemctl", "--user", "enable", "--now", f"secondbrain-{short}.timer"], capture_output=True)
        results.append(f"  [+] {short}")

    for label, script, hour in LAUNCHD_CALENDAR_SERVICES:
        short = label.split(".")[-1]
        service = f"""[Unit]
Description=Second Brain {short}

[Service]
ExecStart={venv_python} {plugin_root}/scripts/{script}
Environment=SECOND_BRAIN_HOME={sb_home}
Environment=CLAUDE_PLUGIN_ROOT={plugin_root}
WorkingDirectory={sb_home}
Type=oneshot
"""
        timer = f"""[Unit]
Description=Second Brain {short} timer

[Timer]
OnCalendar=*-*-* {hour:02d}:00:00

[Install]
WantedBy=timers.target
"""
        (unit_dir / f"secondbrain-{short}.service").write_text(service)
        (unit_dir / f"secondbrain-{short}.timer").write_text(timer)
        subprocess.run(["systemctl", "--user", "enable", "--now", f"secondbrain-{short}.timer"], capture_output=True)
        results.append(f"  [+] {short}")

    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
    return "\n".join(results)


def _uninstall_systemd():
    results = []
    for label, _, _ in LAUNCHD_SERVICES + LAUNCHD_CALENDAR_SERVICES:
        short = label.split(".")[-1]
        subprocess.run(["systemctl", "--user", "disable", "--now", f"secondbrain-{short}.timer"], capture_output=True)
        for suffix in [".service", ".timer"]:
            path = Path.home() / ".config" / "systemd" / "user" / f"secondbrain-{short}{suffix}"
            if path.exists():
                path.unlink()
        results.append(f"  [-] {short}")
    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
    return "\n".join(results)


def _status_systemd():
    lines = []
    for label, _, _ in LAUNCHD_SERVICES + LAUNCHD_CALENDAR_SERVICES:
        short = label.split(".")[-1]
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", f"secondbrain-{short}.timer"],
                capture_output=True, text=True,
            )
            state = result.stdout.strip() or "unknown"
        except Exception:
            state = "unknown"
        lines.append(f"  {short:<12} {state}")
    return "\n".join(lines)
