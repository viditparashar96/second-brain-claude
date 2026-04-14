"""Database abstraction — SQLite + sqlite-vec + FTS5."""

import sqlite3
import struct
import sys
from pathlib import Path

import sqlite_vec

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DB_PATH

EMBEDDING_DIM = 384


def serialize_embedding(embedding):
    return struct.pack(f"{len(embedding)}f", *embedding)


class MemoryDB:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._create_schema()

    def _create_schema(self):
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT NOT NULL,
            heading_path TEXT NOT NULL DEFAULT '', content TEXT NOT NULL,
            line_start INTEGER DEFAULT 0, line_end INTEGER DEFAULT 0, updated_at TEXT NOT NULL)""")
        cur.execute(f"""CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
            chunk_id INTEGER PRIMARY KEY, embedding float[{EMBEDDING_DIM}])""")
        cur.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            content, heading_path, file_path, content_rowid='id')""")
        cur.execute("""CREATE TABLE IF NOT EXISTS file_meta (
            file_path TEXT PRIMARY KEY, mtime REAL NOT NULL, chunk_count INTEGER DEFAULT 0)""")
        self.conn.commit()

    def get_file_mtime(self, file_path):
        row = self.conn.execute("SELECT mtime FROM file_meta WHERE file_path = ?", (file_path,)).fetchone()
        return row[0] if row else None

    def upsert_file_meta(self, file_path, mtime, chunk_count):
        self.conn.execute("INSERT OR REPLACE INTO file_meta VALUES (?, ?, ?)", (file_path, mtime, chunk_count))
        self.conn.commit()

    def delete_file_chunks(self, file_path):
        ids = [r[0] for r in self.conn.execute("SELECT id FROM chunks WHERE file_path = ?", (file_path,))]
        if ids:
            ph = ",".join("?" * len(ids))
            self.conn.execute(f"DELETE FROM chunks_vec WHERE chunk_id IN ({ph})", ids)
            self.conn.execute(f"DELETE FROM chunks_fts WHERE rowid IN ({ph})", ids)
            self.conn.execute(f"DELETE FROM chunks WHERE id IN ({ph})", ids)
        self.conn.execute("DELETE FROM file_meta WHERE file_path = ?", (file_path,))
        self.conn.commit()

    def insert_chunk(self, file_path, heading_path, content, embedding, line_start, line_end, updated_at):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO chunks (file_path, heading_path, content, line_start, line_end, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (file_path, heading_path, content, line_start, line_end, updated_at))
        chunk_id = cur.lastrowid
        cur.execute("INSERT INTO chunks_vec (chunk_id, embedding) VALUES (?, ?)", (chunk_id, serialize_embedding(embedding)))
        cur.execute("INSERT INTO chunks_fts (rowid, content, heading_path, file_path) VALUES (?, ?, ?, ?)",
                    (chunk_id, content, heading_path, file_path))
        return chunk_id

    def commit(self):
        self.conn.commit()

    def vector_search(self, query_embedding, top_k=10, path_prefix=""):
        blob = serialize_embedding(query_embedding)
        if path_prefix:
            rows = self.conn.execute(
                "SELECT v.chunk_id, v.distance, c.file_path, c.heading_path, c.content FROM chunks_vec v JOIN chunks c ON c.id = v.chunk_id WHERE c.file_path LIKE ? ORDER BY v.distance LIMIT ?",
                (f"{path_prefix}%", top_k)).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT v.chunk_id, v.distance, c.file_path, c.heading_path, c.content FROM chunks_vec v JOIN chunks c ON c.id = v.chunk_id WHERE v.embedding MATCH ? AND k = ? ORDER BY v.distance",
                (blob, top_k)).fetchall()
        return [{"id": r[0], "score": 1.0 - (r[1] / 2.0), "file_path": r[2], "heading_path": r[3], "content": r[4]} for r in rows]

    def keyword_search(self, query, top_k=10, path_prefix=""):
        safe = query.replace('"', '""')
        if path_prefix:
            rows = self.conn.execute(
                'SELECT f.rowid, bm25(chunks_fts), c.file_path, c.heading_path, c.content FROM chunks_fts f JOIN chunks c ON c.id = f.rowid WHERE chunks_fts MATCH ? AND c.file_path LIKE ? ORDER BY rank LIMIT ?',
                (f'"{safe}"', f"{path_prefix}%", top_k)).fetchall()
        else:
            rows = self.conn.execute(
                'SELECT f.rowid, bm25(chunks_fts), c.file_path, c.heading_path, c.content FROM chunks_fts f JOIN chunks c ON c.id = f.rowid WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?',
                (f'"{safe}"', top_k)).fetchall()
        return [{"id": r[0], "score": min(1.0, -r[1] / 10.0), "file_path": r[2], "heading_path": r[3], "content": r[4]} for r in rows]

    def get_indexed_files(self):
        return [{"file_path": r[0], "mtime": r[1], "chunk_count": r[2]}
                for r in self.conn.execute("SELECT file_path, mtime, chunk_count FROM file_meta ORDER BY file_path")]

    def close(self):
        self.conn.close()
