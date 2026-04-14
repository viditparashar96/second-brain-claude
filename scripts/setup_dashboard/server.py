"""
Second Brain Setup Dashboard — One-click integration setup.

Run: python3 server.py
Opens localhost:3141 with a setup dashboard for profile + integrations.
"""

import json
import os
import signal
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import urlencode

# Resolve paths before any plugin imports
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    SECOND_BRAIN_HOME, VAULT_DIR, CONFIG_FILE,
    ensure_dirs, load_config, save_config,
)
from auth_handlers import (
    get_google_auth_url, handle_google_callback,
    verify_gmail, verify_gcal, verify_github, verify_asana,
    save_token_to_env, COMBINED_GOOGLE_SCOPES, GMAIL_SCOPES,
    CALENDAR_SCOPES,
)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

PORT = 3141
DASHBOARD_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Second Brain Setup")
app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(DASHBOARD_DIR / "templates"))

# ---------- Pages ----------

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the setup dashboard."""
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    """Post-setup success page."""
    return templates.TemplateResponse(
        request=request, name="dashboard.html",
        context={"setup_complete": True},
    )


# ---------- API: Status ----------

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/status")
async def status():
    """Return current config and integration connection status."""
    config = load_config()
    user = config.get("user", {})
    integrations_config = config.get("integrations", {})

    # Check live status of each integration
    gmail_status = verify_gmail()
    gcal_status = verify_gcal()

    # GitHub and Asana: check from env
    github_token = os.environ.get("GITHUB_TOKEN", "")
    asana_token = os.environ.get("ASANA_TOKEN", "")

    github_status = {"connected": bool(github_token)}
    if github_token:
        github_status = verify_github(github_token)

    asana_status = {"connected": bool(asana_token)}
    if asana_token:
        asana_status = verify_asana(asana_token)

    return {
        "setup_complete": config.get("setup_complete", False),
        "user": {
            "name": user.get("name", ""),
            "role": user.get("role", ""),
            "timezone": user.get("timezone", ""),
        },
        "proactivity": config.get("proactivity", "assistant"),
        "memory_level": config.get("memory_level", "full"),
        "integrations": {
            "gmail": gmail_status,
            "gcal": gcal_status,
            "github": github_status,
            "asana": asana_status,
            "slack": {"connected": False, "coming_soon": True},
        },
    }


# ---------- API: Profile ----------

@app.post("/api/profile")
async def save_profile(request: Request):
    """Save user profile to config.json."""
    data = await request.json()
    config = load_config()

    config["user"] = {
        "name": data.get("name", "").strip(),
        "role": data.get("role", "").strip(),
        "timezone": data.get("timezone", "").strip(),
    }
    config["proactivity"] = data.get("proactivity", "assistant")
    config["memory_level"] = data.get("memory_level", "full")

    save_config(config)
    return {"status": "saved"}


# ---------- API: Google OAuth (Gmail + Calendar) ----------

@app.get("/api/auth/google")
async def google_auth_start(scopes: str = "all"):
    """Start Google OAuth flow. scopes: 'gmail', 'gcal', or 'all'."""
    if scopes == "gmail":
        target_scopes = GMAIL_SCOPES
    elif scopes == "gcal":
        target_scopes = CALENDAR_SCOPES
    elif scopes == "all":
        target_scopes = COMBINED_GOOGLE_SCOPES
    else:
        target_scopes = COMBINED_GOOGLE_SCOPES

    try:
        auth_url = get_google_auth_url(target_scopes)
        return RedirectResponse(url=auth_url)
    except FileNotFoundError:
        return RedirectResponse(url="/?google_setup=needed")


@app.get("/api/auth/google/callback")
async def google_auth_callback(code: str = "", error: str = ""):
    """Handle Google OAuth callback."""
    if error:
        return RedirectResponse(url=f"/?auth_error={error}")

    if not code:
        return RedirectResponse(url="/?auth_error=no_code")

    try:
        result = handle_google_callback(code)
        services = ",".join(result.get("services", []))
        return RedirectResponse(url=f"/?auth_success=google&services={services}")
    except Exception as e:
        return RedirectResponse(url=f"/?auth_error={str(e)[:100]}")


# ---------- API: GitHub ----------

@app.post("/api/auth/github")
async def github_auth(request: Request):
    """Verify and save GitHub PAT."""
    data = await request.json()
    token = data.get("token", "").strip()

    if not token:
        return JSONResponse({"connected": False, "error": "No token provided"}, status_code=400)

    result = verify_github(token)
    if result["connected"]:
        save_token_to_env("GITHUB_TOKEN", token)
        # Update config
        config = load_config()
        config.setdefault("integrations", {})["github"] = {"enabled": True}
        save_config(config)

    return result


# ---------- API: Asana ----------

@app.post("/api/auth/asana")
async def asana_auth(request: Request):
    """Verify and save Asana PAT."""
    data = await request.json()
    token = data.get("token", "").strip()

    if not token:
        return JSONResponse({"connected": False, "error": "No token provided"}, status_code=400)

    result = verify_asana(token)
    if result["connected"]:
        save_token_to_env("ASANA_TOKEN", token)
        # Update config
        config = load_config()
        config.setdefault("integrations", {})["asana"] = {"enabled": True}
        save_config(config)

    return result


# ---------- API: Complete Setup ----------

@app.post("/api/complete")
async def complete_setup(request: Request):
    """Finalize setup: create vault, update config, index."""
    data = await request.json()
    config = load_config()

    # Save profile if included
    if data.get("user"):
        config["user"] = data["user"]
    if data.get("proactivity"):
        config["proactivity"] = data["proactivity"]

    # Create vault directory structure
    ensure_dirs()

    # Copy templates to vault if files don't exist
    templates_dir = PLUGIN_ROOT / "templates"
    vault_files = {
        "SOUL.md": "SOUL.md",
        "USER.md": "USER.md",
        "MEMORY.md": "MEMORY.md",
        "HABITS.md": "HABITS.md",
        "HEARTBEAT.md": "HEARTBEAT.md",
        "ORG.md": "ORG.md",
        "PRODUCTS.md": "PRODUCTS.md",
    }

    created_files = []
    for template_name, vault_name in vault_files.items():
        template_path = templates_dir / template_name
        vault_path = VAULT_DIR / vault_name
        if not vault_path.exists() and template_path.exists():
            content = template_path.read_text()
            # Customize with user info
            user = config.get("user", {})
            content = content.replace("{{NAME}}", user.get("name", "User"))
            content = content.replace("{{USER_NAME}}", user.get("name", "User"))
            content = content.replace("{{USER_ROLE}}", user.get("role", "Developer"))
            content = content.replace("{{ROLE}}", user.get("role", "Developer"))
            content = content.replace("{{TIMEZONE}}", user.get("timezone", "UTC"))
            content = content.replace("{{PROACTIVITY_LEVEL}}", config.get("proactivity", "advisor"))
            vault_path.write_text(content)
            created_files.append(vault_name)

    # Update integration flags based on live status
    gmail_status = verify_gmail()
    gcal_status = verify_gcal()
    github_connected = bool(os.environ.get("GITHUB_TOKEN"))
    asana_connected = bool(os.environ.get("ASANA_TOKEN"))

    config["integrations"] = {
        "gmail": {"enabled": gmail_status.get("connected", False)},
        "gcal": {"enabled": gcal_status.get("connected", False)},
        "github": {"enabled": github_connected},
        "asana": {"enabled": asana_connected},
        "slack": {"enabled": False},
    }

    config["setup_complete"] = True
    save_config(config)

    # Try to index vault (non-blocking)
    try:
        import subprocess
        index_script = SCRIPTS_DIR / "memory_index.py"
        if index_script.exists():
            venv_python = SECOND_BRAIN_HOME / ".venv" / "bin" / "python3"
            python_cmd = str(venv_python) if venv_python.exists() else sys.executable
            subprocess.Popen(
                [python_cmd, str(index_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass  # Indexing is optional at setup time

    # Schedule server shutdown after response
    def shutdown_later():
        import time
        time.sleep(2)
        os.kill(os.getpid(), signal.SIGTERM)

    if data.get("shutdown", True):
        threading.Thread(target=shutdown_later, daemon=True).start()

    return {
        "status": "complete",
        "vault_path": str(VAULT_DIR),
        "config_path": str(CONFIG_FILE),
        "created_files": created_files,
        "integrations": config["integrations"],
    }


# ---------- Startup ----------

def open_browser():
    """Open browser after short delay to let server start."""
    import time
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    print(f"\n  Second Brain Setup Dashboard")
    print(f"  http://localhost:{PORT}")
    print(f"  Press Ctrl+C to quit\n")

    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
