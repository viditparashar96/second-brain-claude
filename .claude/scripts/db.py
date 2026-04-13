"""
Database abstraction layer — SQLite + sqlite-vec + FTS5.

Handles schema creation, chunk storage (with embeddings), vector search,
keyword search, and file metadata tracking for incremental indexing.
"""

import sqlite3
import struct
from pathlib import Path

import sqlite_vec

# 384 dimensions for all-MiniLM-L6-v2
EMBEDDING_DIM = 384

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "memory.db"


def serialize_embedding(embedding) -> bytes:
    """Convert a numpy array or list of floats to a sqlite-vec compatible blob."""
    return struct.pack(f"{len(embedding)}f", *embedding)


def deserialize_embedding(blob: bytes) -> list[float]:
    """Convert a sqlite-vec blob back to a list of floats."""
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


class MemoryDB:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._create_schema()

    def _create_schema(self):
        cur = self.conn.cursor()

        # Main chunks table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                heading_path TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL,
                line_start INTEGER DEFAULT 0,
                line_end INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL
            )
        """)

        # Virtual table for vector search (sqlite-vec)
        cur.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
                chunk_id INTEGER PRIMARY KEY,
                embedding float[{EMBEDDING_DIM}]
            )
        """)

        # Virtual table for full-text search (FTS5)
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                content, heading_path, file_path,
                content_rowid='id'
            )
        """)

        # File metadata for incremental indexing
        cur.execute("""
            CREATE TABLE IF NOT EXISTS file_meta (
                file_path TEXT PRIMARY KEY,
                mtime REAL NOT NULL,
                chunk_count INTEGER DEFAULT 0
            )
        """)

        self.conn.commit()

    def get_file_mtime(self, file_path: str) -> float | None:
        """Get the stored mtime for a file. Returns None if not indexed."""
        cur = self.conn.execute(
            "SELECT mtime FROM file_meta WHERE file_path = ?", (file_path,)
        )
        row = cur.fetchone()
        return row[0] if row else None

    def upsert_file_meta(self, file_path: str, mtime: float, chunk_count: int):
        """Insert or update file metadata."""
        self.conn.execute(
            "INSERT OR REPLACE INTO file_meta (file_path, mtime, chunk_count) VALUES (?, ?, ?)",
            (file_path, mtime, chunk_count),
        )
        self.conn.commit()

    def delete_file_chunks(self, file_path: str):
        """Remove all chunks for a file (before re-indexing it)."""
        cur = self.conn.cursor()

        # Get chunk IDs for this file
        ids = [
            row[0]
            for row in cur.execute(
                "SELECT id FROM chunks WHERE file_path = ?", (file_path,)
            )
        ]

        if ids:
            placeholders = ",".join("?" * len(ids))
            cur.execute(f"DELETE FROM chunks_vec WHERE chunk_id IN ({placeholders})", ids)
            cur.execute(f"DELETE FROM chunks_fts WHERE rowid IN ({placeholders})", ids)
            cur.execute(f"DELETE FROM chunks WHERE id IN ({placeholders})", ids)

        cur.execute("DELETE FROM file_meta WHERE file_path = ?", (file_path,))
        self.conn.commit()

    def insert_chunk(
        self,
        file_path: str,
        heading_path: str,
        content: str,
        embedding,
        line_start: int,
        line_end: int,
        updated_at: str,
    ) -> int:
        """Insert a single chunk with its embedding. Returns the chunk ID."""
        cur = self.conn.cursor()

        cur.execute(
            """INSERT INTO chunks (file_path, heading_path, content, line_start, line_end, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (file_path, heading_path, content, line_start, line_end, updated_at),
        )
        chunk_id = cur.lastrowid

        # Insert into vector index
        cur.execute(
            "INSERT INTO chunks_vec (chunk_id, embedding) VALUES (?, ?)",
            (chunk_id, serialize_embedding(embedding)),
        )

        # Insert into FTS index
        cur.execute(
            "INSERT INTO chunks_fts (rowid, content, heading_path, file_path) VALUES (?, ?, ?, ?)",
            (chunk_id, content, heading_path, file_path),
        )

        return chunk_id

    def commit(self):
        self.conn.commit()

    def vector_search(self, query_embedding, top_k: int = 10, path_prefix: str = "") -> list[dict]:
        """Search by vector similarity. Returns list of {id, file_path, heading_path, content, score}."""
        blob = serialize_embedding(query_embedding)

        if path_prefix:
            rows = self.conn.execute(
                """
                SELECT v.chunk_id, v.distance, c.file_path, c.heading_path, c.content
                FROM chunks_vec v
                JOIN chunks c ON c.id = v.chunk_id
                WHERE c.file_path LIKE ?
                ORDER BY v.distance
                LIMIT ?
                """,
                (f"{path_prefix}%", top_k),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT v.chunk_id, v.distance, c.file_path, c.heading_path, c.content
                FROM chunks_vec v
                JOIN chunks c ON c.id = v.chunk_id
                WHERE v.embedding MATCH ?
                  AND k = ?
                ORDER BY v.distance
                """,
                (blob, top_k),
            ).fetchall()

        results = []
        for row in rows:
            # sqlite-vec returns cosine distance (0 = identical, 2 = opposite)
            # Convert to similarity score: 1 - (distance / 2)
            distance = row[1]
            score = 1.0 - (distance / 2.0)
            results.append({
                "id": row[0],
                "score": score,
                "file_path": row[2],
                "heading_path": row[3],
                "content": row[4],
            })
        return results

    def keyword_search(self, query: str, top_k: int = 10, path_prefix: str = "") -> list[dict]:
        """Search by keyword (FTS5). Returns list of {id, file_path, heading_path, content, score}."""
        # Escape FTS5 special characters
        safe_query = query.replace('"', '""')

        if path_prefix:
            rows = self.conn.execute(
                """
                SELECT f.rowid, bm25(chunks_fts) AS rank, c.file_path, c.heading_path, c.content
                FROM chunks_fts f
                JOIN chunks c ON c.id = f.rowid
                WHERE chunks_fts MATCH ?
                  AND c.file_path LIKE ?
                ORDER BY rank
                LIMIT ?
                """,
                (f'"{safe_query}"', f"{path_prefix}%", top_k),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT f.rowid, bm25(chunks_fts) AS rank, c.file_path, c.heading_path, c.content
                FROM chunks_fts f
                JOIN chunks c ON c.id = f.rowid
                WHERE chunks_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (f'"{safe_query}"', top_k),
            ).fetchall()

        results = []
        for row in rows:
            # BM25 returns negative scores (lower = better match)
            # Normalize to 0-1 range (approximate)
            raw_score = -row[1]
            score = min(1.0, raw_score / 10.0)
            results.append({
                "id": row[0],
                "score": score,
                "file_path": row[2],
                "heading_path": row[3],
                "content": row[4],
            })
        return results

    def get_indexed_files(self) -> list[dict]:
        """List all indexed files with their metadata."""
        rows = self.conn.execute(
            "SELECT file_path, mtime, chunk_count FROM file_meta ORDER BY file_path"
        ).fetchall()
        return [
            {"file_path": r[0], "mtime": r[1], "chunk_count": r[2]}
            for r in rows
        ]

    def close(self):
        self.conn.close()
