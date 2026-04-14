#!/usr/bin/env python3
"""
Dependency Manager — Ensures a plugin-local venv exists with all required packages.

Called by hooks and scripts before importing third-party modules.
Creates ~/.second-brain/.venv/ on first run, installs requirements.txt.

Usage:
    # At the top of any script that needs third-party packages:
    import ensure_deps
    ensure_deps.activate()
    # Now safe to import fastembed, sqlite_vec, etc.
"""

import os
import subprocess
import sys
from pathlib import Path

SECOND_BRAIN_HOME = Path(os.environ.get("SECOND_BRAIN_HOME", Path.home() / ".second-brain"))
VENV_DIR = SECOND_BRAIN_HOME / ".venv"
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))
REQUIREMENTS = PLUGIN_ROOT / "requirements.txt"
MARKER = VENV_DIR / ".deps_installed"


def get_venv_python() -> str:
    """Get path to the venv python executable."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python3")


def get_venv_site_packages() -> str:
    """Get the venv site-packages path."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Lib" / "site-packages")
    # Find the python version dir
    lib_dir = VENV_DIR / "lib"
    if lib_dir.exists():
        for d in lib_dir.iterdir():
            if d.name.startswith("python"):
                return str(d / "site-packages")
    return ""


def ensure_venv():
    """Create venv if it doesn't exist."""
    if not VENV_DIR.exists():
        SECOND_BRAIN_HOME.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True, capture_output=True,
        )


def ensure_packages():
    """Install packages from requirements.txt if not already done."""
    if MARKER.exists() and REQUIREMENTS.exists():
        # Check if requirements.txt changed since last install
        req_mtime = REQUIREMENTS.stat().st_mtime
        marker_mtime = MARKER.stat().st_mtime
        if marker_mtime >= req_mtime:
            return  # Already up to date

    if not REQUIREMENTS.exists():
        return

    venv_python = get_venv_python()
    subprocess.run(
        [venv_python, "-m", "pip", "install", "-q", "-r", str(REQUIREMENTS)],
        check=True, capture_output=True,
    )

    # Write marker
    MARKER.write_text(str(REQUIREMENTS.stat().st_mtime))


def activate():
    """Activate the venv by adding its site-packages to sys.path.

    Call this at the top of any script before importing third-party packages.
    Creates the venv and installs deps on first run.
    """
    ensure_venv()
    ensure_packages()

    site_packages = get_venv_site_packages()
    if site_packages and site_packages not in sys.path:
        sys.path.insert(0, site_packages)
