#!/usr/bin/env python3
"""Incremental Memory Indexer — scans vault, chunks + embeds changed files."""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VAULT_DIR, DB_PATH
from db import MemoryDB
from embeddings import chunk_markdown, embed_texts


def find_md_files(vault_path):
    vault = Path(vault_path)
    if not vault.exists():
        print(f"Vault not found: {vault_path}", file=sys.stderr)
        sys.exit(1)
    return sorted(vault.rglob("*.md"))


def index_file(db, file_path, rel_path):
    text = file_path.read_text(encoding="utf-8")
    if not text.strip():
        return 0
    chunks = chunk_markdown(rel_path, text)
    if not chunks:
        return 0
    embeddings = embed_texts([c.content for c in chunks])
    now = datetime.now().isoformat()
    for chunk, emb in zip(chunks, embeddings):
        db.insert_chunk(chunk.file_path, chunk.heading_path, chunk.content, emb, chunk.line_start, chunk.line_end, now)
    return len(chunks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-path", default=str(VAULT_DIR))
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    start = time.time()
    db = MemoryDB(args.db_path)
    md_files = find_md_files(args.vault_path)
    indexed, skipped, total_chunks = 0, 0, 0
    existing = set()

    for fp in md_files:
        rel = str(fp.relative_to(args.vault_path))
        existing.add(rel)
        mtime = fp.stat().st_mtime
        stored = db.get_file_mtime(rel)
        if not args.force and stored and mtime <= stored:
            skipped += 1
            continue
        db.delete_file_chunks(rel)
        count = index_file(db, fp, rel)
        db.upsert_file_meta(rel, mtime, count)
        db.commit()
        indexed += 1
        total_chunks += count

    removed = 0
    for meta in db.get_indexed_files():
        if meta["file_path"] not in existing:
            db.delete_file_chunks(meta["file_path"])
            removed += 1

    print(f"Indexing complete in {time.time() - start:.1f}s")
    print(f"  Files indexed: {indexed} ({total_chunks} chunks)")
    print(f"  Files skipped: {skipped}")
    if removed:
        print(f"  Files removed: {removed}")
    db.close()


if __name__ == "__main__":
    main()
