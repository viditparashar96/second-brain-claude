"""
Second Brain Config — Dynamic path resolution for plugin deployment.

All paths resolve relative to:
- SECOND_BRAIN_HOME: ~/.second-brain/ (vault, config, data)
- PLUGIN_ROOT: ${CLAUDE_PLUGIN_ROOT} (plugin scripts, templates)

Config stored at: ~/.second-brain/config.json
Vault stored at: ~/.second-brain/vault/
Data stored at: ~/.second-brain/data/
"""

import json
import os
import sys
from pathlib import Path

# Auto-activate plugin venv before any third-party imports
try:
    from ensure_deps import activate
    activate()
except Exception:
    pass  # First run or ensure_deps not yet available

# Core paths
SECOND_BRAIN_HOME = Path(os.environ.get("SECOND_BRAIN_HOME", Path.home() / ".second-brain"))
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent))

# Derived paths
VAULT_DIR = SECOND_BRAIN_HOME / "vault"
CONFIG_FILE = SECOND_BRAIN_HOME / "config.json"
DATA_DIR = SECOND_BRAIN_HOME / "data"
DB_PATH = DATA_DIR / "memory.db"
STATE_DIR = DATA_DIR / "state"
LOG_DIR = DATA_DIR / "logs"
CREDENTIALS_DIR = DATA_DIR / "credentials"
MODEL_CACHE_DIR = DATA_DIR / "model_cache"

# Vault subdirectories
DAILY_DIR = VAULT_DIR / "daily"
MEETINGS_DIR = VAULT_DIR / "meetings"
PROJECTS_DIR = VAULT_DIR / "projects"
CLIENTS_DIR = VAULT_DIR / "clients"
TEAM_DIR = VAULT_DIR / "team"
RESEARCH_DIR = VAULT_DIR / "research"
CONTENT_DIR = VAULT_DIR / "content"
DRAFTS_DIR = VAULT_DIR / "drafts"


def ensure_dirs():
    """Create all required directories if they don't exist."""
    for d in [
        VAULT_DIR, DATA_DIR, STATE_DIR, LOG_DIR, CREDENTIALS_DIR,
        MODEL_CACHE_DIR, DAILY_DIR, MEETINGS_DIR, PROJECTS_DIR,
        CLIENTS_DIR, TEAM_DIR, RESEARCH_DIR, CONTENT_DIR,
        DRAFTS_DIR / "active", DRAFTS_DIR / "sent", DRAFTS_DIR / "expired",
    ]:
        d.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load user config from ~/.second-brain/config.json."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}


def save_config(config: dict):
    """Save user config to ~/.second-brain/config.json."""
    SECOND_BRAIN_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_user_name() -> str:
    config = load_config()
    return config.get("user", {}).get("name", "User")


def get_timezone() -> str:
    config = load_config()
    return config.get("user", {}).get("timezone", "UTC")


def get_enabled_integrations() -> list[str]:
    config = load_config()
    integrations = config.get("integrations", {})
    return [name for name, cfg in integrations.items() if cfg.get("enabled", False)]


def get_proactivity_level() -> str:
    config = load_config()
    return config.get("proactivity", "advisor")


def get_memory_level() -> str:
    """Get the memory level: 'full', 'light', or 'off'.

    full  = SessionStart + Stop (CLI) + PreCompact + SessionEnd + guardrails
    light = SessionStart + PreCompact + SessionEnd + guardrails (no Stop hook)
    off   = Only guardrails (security)
    """
    config = load_config()
    return config.get("memory_level", "full")


def is_setup_complete() -> bool:
    """Check if the initial setup has been run."""
    return CONFIG_FILE.exists() and load_config().get("setup_complete", False)


# Load .env from second-brain home if it exists
_env_path = SECOND_BRAIN_HOME / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(str(_env_path))
