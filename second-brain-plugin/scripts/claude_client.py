"""Shared Claude Client — Auto-detects Bedrock vs direct Anthropic API."""

import os
from pathlib import Path

sys_path = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(sys_path))
from config import SECOND_BRAIN_HOME

# Load .env
_env_path = SECOND_BRAIN_HOME / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(str(_env_path))

BEDROCK_MODEL_CANDIDATES = [
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
]
DIRECT_MODEL_ID = "claude-sonnet-4-5-20250514"

_client = None
_model_id = None
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


def get_client():
    global _client, _model_id, _initialized
    if _initialized:
        return _client
    _initialized = True

    import anthropic

    aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    aws_region = os.environ.get("AWS_REGION", "us-east-1")

    if aws_key and aws_secret:
        _client = anthropic.AnthropicBedrock(aws_access_key=aws_key, aws_secret_key=aws_secret, aws_region=aws_region)
        _model_id = _probe_bedrock_model(_client)
        return _client

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        _client = anthropic.Anthropic(api_key=api_key)
        _model_id = DIRECT_MODEL_ID
        return _client

    return None


def get_model_id():
    global _model_id
    if _model_id is None:
        get_client()
    return _model_id or DIRECT_MODEL_ID


def create_message(system, messages, max_tokens=1000):
    client = get_client()
    if not client:
        return None
    response = client.messages.create(model=get_model_id(), max_tokens=max_tokens, system=system, messages=messages)
    return response.content[0].text
