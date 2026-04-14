"""
Shared Claude Client — Auto-detects the best available Claude access method.

Priority:
1. AWS Bedrock (AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY)
2. Anthropic API (ANTHROPIC_API_KEY)
3. Claude CLI (claude --print) — free with Claude Max subscription

Usage:
    from claude_client import create_message
    result = create_message(system="...", messages=[...])
    # Returns None only if ALL three methods are unavailable
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import SECOND_BRAIN_HOME

# Load .env
_env_path = SECOND_BRAIN_HOME / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(str(_env_path))
    except ImportError:
        pass

BEDROCK_MODEL_CANDIDATES = [
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
]
DIRECT_MODEL_ID = "claude-sonnet-4-5-20250514"

_client = None
_model_id = None
_mode = None  # "bedrock", "direct", "cli", or None
_initialized = False


def _probe_bedrock_model(client):
    override = os.environ.get("BEDROCK_MODEL_ID", "")
    if override:
        return override
    for model_id in BEDROCK_MODEL_CANDIDATES:
        try:
            client.messages.create(model=model_id, max_tokens=5, messages=[{"role": "user", "content": "hi"}])
            return model_id
        except Exception:
            continue
    return BEDROCK_MODEL_CANDIDATES[-1]


def _call_cli(system, user_message, max_tokens=1000):
    """Use Claude CLI (claude --print) for LLM calls. Free with Claude Max."""
    claude_path = shutil.which("claude")
    if not claude_path:
        return None

    prompt = user_message
    if system:
        prompt = f"System: {system}\n\n{user_message}"

    try:
        result = subprocess.run(
            [claude_path, "--print", "-p", prompt],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_client():
    global _client, _model_id, _mode, _initialized
    if _initialized:
        return _client
    _initialized = True

    # Try Bedrock first
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")

    if aws_key and aws_secret:
        try:
            import anthropic
            _client = anthropic.AnthropicBedrock(aws_access_key=aws_key, aws_secret_key=aws_secret, aws_region=aws_region)
            _model_id = _probe_bedrock_model(_client)
            _mode = "bedrock"
            return _client
        except ImportError:
            pass

    # Try direct API
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        try:
            import anthropic
            _client = anthropic.Anthropic(api_key=api_key)
            _model_id = DIRECT_MODEL_ID
            _mode = "direct"
            return _client
        except ImportError:
            pass

    # Check if CLI is available (Claude Max)
    if shutil.which("claude"):
        _mode = "cli"
        return None  # No SDK client, but create_message will use CLI

    return None


def get_model_id():
    global _model_id
    if _model_id is None:
        get_client()
    return _model_id or DIRECT_MODEL_ID


def get_mode():
    """Return the active mode: 'bedrock', 'direct', 'cli', or None."""
    global _mode
    if not _initialized:
        get_client()
    return _mode


def create_message(system, messages, max_tokens=1000):
    """Create a message using the best available method.

    Returns the response text, or None if no method is available.
    """
    client = get_client()

    # SDK-based (Bedrock or direct API)
    if client and _mode in ("bedrock", "direct"):
        response = client.messages.create(
            model=get_model_id(),
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text

    # CLI-based (Claude Max)
    if _mode == "cli":
        # Extract the last user message for the prompt
        user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_msg = msg.get("content", "")
                break
        return _call_cli(system, user_msg, max_tokens)

    return None
