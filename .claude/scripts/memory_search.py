#!/usr/bin/env python3
"""
Hybrid Memory Search CLI — Combines vector similarity (sqlite-vec) and
keyword matching (FTS5) for best-of-both-worlds retrieval.

Usage:
    python memory_search.py "query text" [--top-k N] [--path-prefix PREFIX] [--db-path PATH]

Options:
    --top-k         Number of results to return (default: 5)
    --path-prefix   Only search files matching this prefix (e.g., "drafts/sent")
    --db-path       Path to the SQLite database (default: .claude/data/memory.db)
    --mode          Search mode: hybrid (default), vector, keyword
    --json          Output results as JSON instead of formatted text

Examples:
    python memory_search.py "meeting decisions about deployment"
    python memory_search.py "client email tone" --path-prefix drafts/sent --top-k 3
    python memory_search.py "asana deadline" --mode keyword
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import MemoryDB
from embeddings import embed_query

PROJECT_DIR = os.environ.get(
    "CLAUDE_PROJECT_DIR",
    str(Path(__file__).resolve().parent.parent.parent)
)
DEFAULT_DB = os.path.join(PROJECT_DIR, ".claude", "data", "memory.db")

# Hybrid merge weights
VECTOR_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3


def hybrid_search(
    db: MemoryDB,
    query: str,
    top_k: int = 5,
    path_prefix: str = "",
) -> list[dict]:
    """Run hybrid search: vector + keyword, merged by weighted score."""

    # Get more results from each source, then merge and re-rank
    fetch_k = top_k * 3

    # Vector search
    query_embedding = embed_query(query)
    vec_results = db.vector_search(query_embedding, top_k=fetch_k, path_prefix=path_prefix)

    # Keyword search
    kw_results = db.keyword_search(query, top_k=fetch_k, path_prefix=path_prefix)

    # Merge by chunk ID
    merged: dict[int, dict] = {}

    for r in vec_results:
        merged[r["id"]] = {
            **r,
            "vec_score": r["score"],
            "kw_score": 0.0,
        }

    for r in kw_results:
        if r["id"] in merged:
            merged[r["id"]]["kw_score"] = r["score"]
        else:
            merged[r["id"]] = {
                **r,
                "vec_score": 0.0,
                "kw_score": r["score"],
            }

    # Calculate hybrid score
    for item in merged.values():
        item["score"] = (
            VECTOR_WEIGHT * item["vec_score"] + KEYWORD_WEIGHT * item["kw_score"]
        )

    # Sort by hybrid score, return top-k
    ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:top_k]

    return ranked


def vector_only_search(
    db: MemoryDB, query: str, top_k: int = 5, path_prefix: str = ""
) -> list[dict]:
    query_embedding = embed_query(query)
    return db.vector_search(query_embedding, top_k=top_k, path_prefix=path_prefix)


def keyword_only_search(
    db: MemoryDB, query: str, top_k: int = 5, path_prefix: str = ""
) -> list[dict]:
    return db.keyword_search(query, top_k=top_k, path_prefix=path_prefix)


def format_results(results: list[dict]) -> str:
    """Format results for human-readable terminal output."""
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        score = r["score"]
        path = r["file_path"]
        heading = r["heading_path"]
        content = r["content"]

        # Truncate long content for display
        if len(content) > 200:
            content = content[:200] + "..."

        header = f"[{i}] {path}"
        if heading:
            header += f" > {heading}"
        header += f"  (score: {score:.3f})"

        lines.append(header)
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search the memory vault")
    parser.add_argument("query", help="Search query text")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--path-prefix", default="", help="Filter by file path prefix")
    parser.add_argument("--db-path", default=DEFAULT_DB, help="Path to SQLite database")
    parser.add_argument("--mode", choices=["hybrid", "vector", "keyword"], default="hybrid")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print("Database not found. Run memory_index.py first.", file=sys.stderr)
        sys.exit(1)

    db = MemoryDB(args.db_path)

    if args.mode == "hybrid":
        results = hybrid_search(db, args.query, args.top_k, args.path_prefix)
    elif args.mode == "vector":
        results = vector_only_search(db, args.query, args.top_k, args.path_prefix)
    else:
        results = keyword_only_search(db, args.query, args.top_k, args.path_prefix)

    if args.json:
        # Clean up internal score fields for JSON output
        output = []
        for r in results:
            output.append({
                "file_path": r["file_path"],
                "heading_path": r["heading_path"],
                "content": r["content"],
                "score": round(r["score"], 4),
            })
        print(json.dumps(output, indent=2))
    else:
        print(format_results(results))

    db.close()


if __name__ == "__main__":
    main()
