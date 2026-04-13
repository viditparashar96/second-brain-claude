"""
Shared Claude Client — Auto-detects Bedrock vs direct Anthropic API.

Checks env vars in this order:
1. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY → uses AnthropicBedrock
2. ANTHROPIC_API_KEY → uses direct Anthropic API
3. Neither → returns None

For Bedrock, auto-probes available models from best to fallback.
Set BEDROCK_MODEL_ID in .env to override the auto-probe.

Usage:
    from claude_client import create_message
    result = create_message(system="...", messages=[...])
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent)
)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

# Bedrock model IDs to try, best first (cross-region us. prefix)
BEDROCK_MODEL_CANDIDATES = [
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",  # Legacy fallback
]

DIRECT_MODEL_ID = "claude-sonnet-4-5-20250514"

# Module-level state
_client = None
_model_id = None
_initialized = False


def _probe_bedrock_model(client) -> str:
    """Try model IDs in order, return the first that works."""
    # Allow override via env var
    override = os.environ.get("BEDROCK_MODEL_ID", "")
    if override:
        return override

    for model_id in BEDROCK_MODEL_CANDIDATES:
        try:
            client.messages.create(
                model=model_id,
                max_tokens=5,
                messages=[{"role": "user", "content": "hi"}],
            )
            return model_id
        except Exception:
            continue

    # If nothing works, return the last fallback
    return BEDROCK_MODEL_CANDIDATES[-1]


def get_client():
    """Get an Anthropic client (Bedrock or direct). Returns None if no keys configured."""
    global _client, _model_id, _initialized

    if _initialized:
        return _client

    _initialized = True

    import anthropic

    # Try Bedrock first
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")

    if aws_key and aws_secret:
        _client = anthropic.AnthropicBedrock(
            aws_access_key=aws_key,
            aws_secret_key=aws_secret,
            aws_region=aws_region,
        )
        _model_id = _probe_bedrock_model(_client)
        return _client

    # Fall back to direct API
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        _client = anthropic.Anthropic(api_key=api_key)
        _model_id = DIRECT_MODEL_ID
        return _client

    return None


def get_model_id() -> str:
    """Get the model ID for the configured client."""
    global _model_id
    if _model_id is None:
        get_client()  # Initialize if needed
    return _model_id or DIRECT_MODEL_ID


def create_message(system: str, messages: list[dict], max_tokens: int = 1000) -> str | None:
    """Convenience wrapper: create a message and return the text response.

    Returns None if no client is configured.
    """
    client = get_client()
    if not client:
        return None

    response = client.messages.create(
        model=get_model_id(),
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text
