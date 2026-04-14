#!/usr/bin/env python3
"""Hybrid Memory Search CLI — vector + keyword merge."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DB_PATH
from db import MemoryDB
from embeddings import embed_query

VECTOR_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3


def hybrid_search(db, query, top_k=5, path_prefix=""):
    fetch_k = top_k * 3
    vec_results = db.vector_search(embed_query(query), top_k=fetch_k, path_prefix=path_prefix)
    kw_results = db.keyword_search(query, top_k=fetch_k, path_prefix=path_prefix)

    merged = {}
    for r in vec_results:
        merged[r["id"]] = {**r, "vec_score": r["score"], "kw_score": 0.0}
    for r in kw_results:
        if r["id"] in merged:
            merged[r["id"]]["kw_score"] = r["score"]
        else:
            merged[r["id"]] = {**r, "vec_score": 0.0, "kw_score": r["score"]}

    for item in merged.values():
        item["score"] = VECTOR_WEIGHT * item["vec_score"] + KEYWORD_WEIGHT * item["kw_score"]

    return sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:top_k]


def main():
    parser = argparse.ArgumentParser(description="Search the memory vault")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--path-prefix", default="")
    parser.add_argument("--db-path", default=str(DB_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not Path(args.db_path).exists():
        print("Database not found. Run memory_index.py first.", file=sys.stderr)
        sys.exit(1)

    db = MemoryDB(args.db_path)
    results = hybrid_search(db, args.query, args.top_k, args.path_prefix)

    if args.json:
        print(json.dumps([{"file_path": r["file_path"], "heading_path": r["heading_path"],
                           "content": r["content"], "score": round(r["score"], 4)} for r in results], indent=2))
    else:
        for i, r in enumerate(results, 1):
            header = f"[{i}] {r['file_path']}"
            if r["heading_path"]:
                header += f" > {r['heading_path']}"
            header += f"  (score: {r['score']:.3f})"
            content = r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"]
            print(f"{header}\n{content}\n")
    db.close()


if __name__ == "__main__":
    main()
