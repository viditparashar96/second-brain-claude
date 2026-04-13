"""
Integration Template — Copy this file to create a new integration.

Steps:
1. Copy this file to integrations/<name>/client.py
2. Replace TODOs with your implementation
3. Create auth.py for credential management
4. Create cli.py for CLI subcommands
5. Register in registry.py
"""

import os
from dataclasses import dataclass
from datetime import datetime


# TODO: Define your data model
@dataclass
class Item:
    id: str
    title: str
    body: str
    created_at: datetime
    metadata: dict


# TODO: Implement auth
def get_client():
    """Authenticate and return an API client."""
    raise NotImplementedError


# TODO: Implement query functions
def list_items(client, limit: int = 20) -> list[Item]:
    """List recent items."""
    raise NotImplementedError


def get_item(client, item_id: str) -> Item:
    """Get a single item by ID."""
    raise NotImplementedError


# TODO: Implement context formatter
def format_for_context(items: list[Item]) -> str:
    """Format items for injection into Claude's context."""
    lines = []
    for item in items:
        lines.append(f"- [{item.id}] {item.title} ({item.created_at})")
    return "\n".join(lines)
