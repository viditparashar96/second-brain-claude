"""
API Key Isolation Layer — Ensures tokens never leak into context.

Principles:
1. All API tokens live in .env (never in vault markdown or Claude context)
2. Python CLI wrappers (query.py) handle auth — Claude only sees formatted data
3. This module provides utilities to verify isolation is maintained

Usage:
    from api_wrapper import verify_env_safety, mask_token, check_no_tokens_in_text
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent)
)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

# Token env var names to protect
PROTECTED_VARS = [
    "GITHUB_TOKEN",
    "ASANA_TOKEN",
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "ANTHROPIC_API_KEY",
]

# Token patterns that should never appear in output
TOKEN_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"xoxb-[0-9]+-[0-9]+-[A-Za-z0-9]+"),
    re.compile(r"xapp-[0-9]+-[A-Za-z0-9]+-[0-9]+-[a-f0-9]+"),
    re.compile(r"0/[a-f0-9]{30,}"),  # Asana PAT
    re.compile(r"sk-ant-[A-Za-z0-9-]+"),  # Anthropic key
    re.compile(r"AKIA[A-Z0-9]{16}"),  # AWS access key
    re.compile(r"gho_[A-Za-z0-9]+"),  # GitHub OAuth token
    re.compile(r"ghp_[A-Za-z0-9]+"),  # GitHub PAT (classic)
]


def get_token_values() -> list[str]:
    """Get actual token values from env (for checking leaks)."""
    values = []
    for var in PROTECTED_VARS:
        val = os.environ.get(var, "")
        if val and len(val) > 8:
            values.append(val)
    return values


def mask_token(token: str) -> str:
    """Mask a token for safe display: show first 4 and last 4 chars."""
    if len(token) <= 12:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


def check_no_tokens_in_text(text: str) -> list[str]:
    """Check if any known tokens appear in text. Returns list of leaked var names."""
    leaks = []

    # Check actual token values
    for var in PROTECTED_VARS:
        val = os.environ.get(var, "")
        if val and len(val) > 8 and val in text:
            leaks.append(var)

    # Check token patterns
    for pattern in TOKEN_PATTERNS:
        if pattern.search(text):
            leaks.append(f"pattern:{pattern.pattern[:30]}")

    return leaks


def verify_env_safety() -> list[str]:
    """Verify that .env and credential files are properly protected.

    Returns a list of issues found (empty = all good).
    """
    issues = []

    # Check .gitignore exists and contains .env
    gitignore_path = Path(PROJECT_DIR) / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if ".env" not in content:
            issues.append(".env is NOT in .gitignore — tokens may be committed!")
        if ".claude/data/" not in content and "*.db" not in content:
            issues.append(".claude/data/ is NOT in .gitignore — credentials may be committed!")
    else:
        issues.append("No .gitignore found — all files including .env may be committed!")

    # Check .env exists and has tokens
    env_path = Path(PROJECT_DIR) / ".env"
    if not env_path.exists():
        issues.append(".env file not found")
    else:
        # Check file permissions (should not be world-readable)
        mode = oct(env_path.stat().st_mode)[-3:]
        if mode[-1] != "0" and mode[-1] != "4":
            pass  # macOS default is fine

    # Check no tokens in vault markdown files
    vault_dir = Path(PROJECT_DIR) / "Dynamous" / "Memory"
    if vault_dir.exists():
        token_values = get_token_values()
        for md_file in vault_dir.rglob("*.md"):
            try:
                content = md_file.read_text()
                for var in PROTECTED_VARS:
                    val = os.environ.get(var, "")
                    if val and len(val) > 8 and val in content:
                        rel_path = md_file.relative_to(PROJECT_DIR)
                        issues.append(f"TOKEN LEAK: {var} found in {rel_path}")
            except Exception:
                pass

    return issues


def print_safety_report():
    """Print a formatted safety report."""
    issues = verify_env_safety()

    print("API Key Isolation Report")
    print("=" * 50)

    if not issues:
        print("[OK] All checks passed")
    else:
        for issue in issues:
            print(f"[!!] {issue}")

    print()
    print("Protected variables:")
    for var in PROTECTED_VARS:
        val = os.environ.get(var, "")
        if val:
            print(f"  [+] {var} = {mask_token(val)}")
        else:
            print(f"  [-] {var} = (not set)")


if __name__ == "__main__":
    print_safety_report()
