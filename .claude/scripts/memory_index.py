#!/usr/bin/env python3
"""
Incremental Memory Indexer — Scans the vault, detects changed files,
chunks + embeds only what changed, stores in SQLite.

Usage:
    python memory_index.py [--vault-path PATH] [--db-path PATH] [--force]

Options:
    --vault-path    Path to the vault directory (default: Dynamous/Memory/)
    --db-path       Path to the SQLite database (default: .claude/data/memory.db)
    --force         Re-index all files, ignoring mtime cache
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add scripts dir to path for local imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import MemoryDB
from embeddings import chunk_markdown, embed_texts


PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent)
)
DEFAULT_VAULT = os.path.join(PROJECT_DIR, "Dynamous", "Memory")
DEFAULT_DB = os.path.join(PROJECT_DIR, ".claude", "data", "memory.db")


def find_markdown_files(vault_path: str) -> list[Path]:
    """Find all .md files in the vault."""
    vault = Path(vault_path)
    if not vault.exists():
        print(f"Vault not found: {vault_path}", file=sys.stderr)
        sys.exit(1)
    return sorted(vault.rglob("*.md"))


def get_relative_path(file_path: Path, vault_path: str) -> str:
    """Get a file path relative to the vault root."""
    return str(file_path.relative_to(vault_path))


def index_file(db: MemoryDB, file_path: Path, rel_path: str):
    """Chunk, embed, and store a single file."""
    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return 0

    chunks = chunk_markdown(rel_path, text)
    if not chunks:
        return 0

    # Batch embed all chunks
    texts = [c.content for c in chunks]
    embeddings = embed_texts(texts)

    now = datetime.now().isoformat()

    for chunk, embedding in zip(chunks, embeddings):
        db.insert_chunk(
            file_path=chunk.file_path,
            heading_path=chunk.heading_path,
            content=chunk.content,
            embedding=embedding,
            line_start=chunk.line_start,
            line_end=chunk.line_end,
            updated_at=now,
        )

    return len(chunks)


def main():
    parser = argparse.ArgumentParser(description="Index vault markdown files for RAG search")
    parser.add_argument("--vault-path", default=DEFAULT_VAULT, help="Path to vault directory")
    parser.add_argument("--db-path", default=DEFAULT_DB, help="Path to SQLite database")
    parser.add_argument("--force", action="store_true", help="Re-index all files")
    args = parser.parse_args()

    start_time = time.time()

    db = MemoryDB(args.db_path)
    md_files = find_markdown_files(args.vault_path)

    indexed_count = 0
    skipped_count = 0
    total_chunks = 0

    # Track which files still exist (for cleanup)
    existing_rel_paths = set()

    for file_path in md_files:
        rel_path = get_relative_path(file_path, args.vault_path)
        existing_rel_paths.add(rel_path)

        current_mtime = file_path.stat().st_mtime
        stored_mtime = db.get_file_mtime(rel_path)

        if not args.force and stored_mtime is not None and current_mtime <= stored_mtime:
            skipped_count += 1
            continue

        # File is new or modified — re-index it
        db.delete_file_chunks(rel_path)
        chunk_count = index_file(db, file_path, rel_path)
        db.upsert_file_meta(rel_path, current_mtime, chunk_count)
        db.commit()

        indexed_count += 1
        total_chunks += chunk_count

    # Clean up chunks for deleted files
    removed_count = 0
    for meta in db.get_indexed_files():
        if meta["file_path"] not in existing_rel_paths:
            db.delete_file_chunks(meta["file_path"])
            removed_count += 1

    elapsed = time.time() - start_time

    print(f"Indexing complete in {elapsed:.1f}s")
    print(f"  Files indexed: {indexed_count} ({total_chunks} chunks)")
    print(f"  Files skipped (unchanged): {skipped_count}")
    if removed_count:
        print(f"  Files removed (deleted): {removed_count}")
    print(f"  Total files in index: {len(existing_rel_paths)}")

    db.close()


if __name__ == "__main__":
    main()
