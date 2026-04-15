#!/usr/bin/env python3
"""
Second Brain Setup Launcher

Cross-platform launcher that:
1. Finds the right Python (python3, python, py)
2. Ensures venv + deps are installed
3. Launches the dashboard server

Usage:
  python3 launch.py
  python launch.py
  py launch.py
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
SECOND_BRAIN_HOME = Path(os.environ.get("SECOND_BRAIN_HOME", Path.home() / ".second-brain"))
VENV_DIR = SECOND_BRAIN_HOME / ".venv"
REQUIREMENTS = PLUGIN_ROOT / "requirements.txt"


def find_python() -> str | None:
    """Find a suitable Python >= 3.10 on this system."""
    # Check if current interpreter is good enough
    if sys.version_info >= MIN_PYTHON:
        return sys.executable

    # Try common names
    candidates = ["python3", "python", "py"]
    if platform.system() == "Windows":
        candidates = ["py", "python3", "python"]

    for name in candidates:
        path = shutil.which(name)
        if not path:
            continue
        try:
            result = subprocess.run(
                [path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(".")
                major, minor = int(parts[0]), int(parts[1])
                if (major, minor) >= MIN_PYTHON:
                    return path
        except Exception:
            continue

    return None


def get_venv_python() -> str:
    """Return path to Python inside the venv."""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python3")


def ensure_venv(python: str):
    """Create venv if it doesn't exist."""
    venv_py = get_venv_python()
    if Path(venv_py).exists():
        return

    print("  Creating virtual environment...")
    VENV_DIR.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([python, "-m", "venv", str(VENV_DIR)], check=True)


def ensure_deps():
    """Install dependencies if needed."""
    marker = VENV_DIR / ".deps_installed"
    req_mtime = REQUIREMENTS.stat().st_mtime if REQUIREMENTS.exists() else 0

    if marker.exists():
        try:
            marker_mtime = float(marker.read_text().strip())
            if marker_mtime >= req_mtime:
                return  # Already up to date
        except Exception:
            pass

    print("  Installing dependencies...")
    venv_py = get_venv_python()

    # Get pip path
    if platform.system() == "Windows":
        pip = str(VENV_DIR / "Scripts" / "pip.exe")
    else:
        pip = str(VENV_DIR / "bin" / "pip")

    result = subprocess.run(
        [pip, "install", "-q", "-r", str(REQUIREMENTS)],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print(f"  Warning: some dependencies failed to install:")
        print(f"  {result.stderr[:200]}")
        print(f"  The dashboard may still work for basic setup.")
    else:
        marker.write_text(str(req_mtime))


def main():
    print("\n  Second Brain Setup")
    print("  " + "-" * 30)

    # Step 1: Find Python
    python = find_python()
    if not python:
        print(f"\n  Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required but not found.")
        print()
        system = platform.system()
        if system == "Darwin":
            print("  Install with: brew install python@3.12")
        elif system == "Windows":
            print("  Download from: https://python.org/downloads/")
            print("  IMPORTANT: Check 'Add to PATH' during install")
        else:
            print("  Install with: sudo apt install python3 (Debian/Ubuntu)")
            print("            or: sudo dnf install python3 (Fedora)")
        print()
        sys.exit(1)

    print(f"  Python: {python}")

    # Step 2: Ensure venv
    ensure_venv(python)
    print(f"  Venv: {VENV_DIR}")

    # Step 3: Ensure deps
    ensure_deps()
    print(f"  Dependencies: OK")

    # Step 4: Launch server using venv Python
    venv_py = get_venv_python()
    server_script = Path(__file__).resolve().parent / "server.py"

    print(f"  Launching dashboard...\n")

    os.execv(venv_py, [venv_py, str(server_script)])


if __name__ == "__main__":
    main()
