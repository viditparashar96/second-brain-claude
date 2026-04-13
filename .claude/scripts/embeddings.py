"""
Embeddings module — FastEmbed wrapper with markdown-aware chunking.

Handles:
- Markdown chunking by heading hierarchy + paragraph splitting
- Overlap between consecutive chunks
- FastEmbed model loading with persistent cache
- Batch embedding API
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_DIR = str(Path(__file__).resolve().parent.parent / "data" / "model_cache")

# Chunking parameters
MAX_CHUNK_CHARS = 400  # ~100 tokens — well within 256-token model limit
OVERLAP_CHARS = 80     # ~20 tokens overlap between consecutive chunks

# Singleton model instance (avoid reloading the ONNX model on every call)
_model: TextEmbedding | None = None


def get_model() -> TextEmbedding:
    """Get or create the FastEmbed model (singleton)."""
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=MODEL_NAME, cache_dir=CACHE_DIR)
    return _model


def embed_texts(texts: list[str]) -> list:
    """Embed a list of texts. Returns list of numpy arrays (384-dim each)."""
    model = get_model()
    # embed() returns a generator — must materialize with list()
    return list(model.embed(texts, batch_size=256))


def embed_query(query: str) -> list:
    """Embed a single query string. Returns a numpy array (384-dim)."""
    model = get_model()
    return list(model.embed([query]))[0]


@dataclass
class Chunk:
    """A chunk of text with its source metadata."""
    content: str
    file_path: str
    heading_path: str
    line_start: int
    line_end: int


def chunk_markdown(file_path: str, text: str) -> list[Chunk]:
    """Split markdown text into chunks, preserving heading hierarchy.

    Strategy:
    1. Split by headings (H1/H2/H3) to get sections
    2. Within each section, split long text by paragraphs
    3. If a paragraph is still too long, split by sentences
    4. Add overlap between consecutive chunks
    """
    lines = text.split("\n")
    sections = _split_by_headings(lines)
    chunks = []

    for heading_path, section_lines, start_line in sections:
        section_text = "\n".join(section_lines).strip()
        if not section_text:
            continue

        paragraphs = _split_into_paragraphs(section_text)
        section_chunks = _merge_paragraphs_into_chunks(
            paragraphs, file_path, heading_path, start_line
        )
        chunks.extend(section_chunks)

    # Add overlap between consecutive chunks from the same file
    chunks = _add_overlap(chunks)

    return chunks


def _split_by_headings(lines: list[str]) -> list[tuple[str, list[str], int]]:
    """Split lines into sections by heading. Returns (heading_path, lines, start_line)."""
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$")
    sections: list[tuple[str, list[str], int]] = []

    current_headings = ["", "", ""]  # H1, H2, H3
    current_lines: list[str] = []
    current_start = 0

    for i, line in enumerate(lines):
        match = heading_re.match(line)
        if match:
            # Save previous section
            if current_lines:
                path = " > ".join(h for h in current_headings if h)
                sections.append((path, current_lines, current_start))

            level = len(match.group(1)) - 1  # 0, 1, or 2
            heading_text = match.group(2).strip()
            current_headings[level] = heading_text
            # Clear sub-headings when a higher-level heading appears
            for j in range(level + 1, 3):
                current_headings[j] = ""

            current_lines = []
            current_start = i
        else:
            current_lines.append(line)

    # Don't forget the last section
    if current_lines:
        path = " > ".join(h for h in current_headings if h)
        sections.append((path, current_lines, current_start))

    return sections


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs (double newline separated)."""
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def _merge_paragraphs_into_chunks(
    paragraphs: list[str],
    file_path: str,
    heading_path: str,
    base_line: int,
) -> list[Chunk]:
    """Merge small paragraphs into chunks up to MAX_CHUNK_CHARS."""
    chunks = []
    current_text = ""
    chunk_start = base_line

    for para in paragraphs:
        if not current_text:
            current_text = para
            continue

        combined = current_text + "\n\n" + para
        if len(combined) <= MAX_CHUNK_CHARS:
            current_text = combined
        else:
            # Current chunk is full — save it
            chunks.append(Chunk(
                content=current_text,
                file_path=file_path,
                heading_path=heading_path,
                line_start=chunk_start,
                line_end=chunk_start + current_text.count("\n"),
            ))
            chunk_start += current_text.count("\n") + 2
            current_text = para

    # Save the last chunk
    if current_text:
        chunks.append(Chunk(
            content=current_text,
            file_path=file_path,
            heading_path=heading_path,
            line_start=chunk_start,
            line_end=chunk_start + current_text.count("\n"),
        ))

    return chunks


def _add_overlap(chunks: list[Chunk]) -> list[Chunk]:
    """Add text overlap between consecutive chunks from the same file.

    Prepends the last OVERLAP_CHARS of the previous chunk to the current one.
    This helps the embedding model capture context across chunk boundaries.
    """
    if len(chunks) <= 1:
        return chunks

    result = [chunks[0]]
    for i in range(1, len(chunks)):
        prev = chunks[i - 1]
        curr = chunks[i]

        if prev.file_path == curr.file_path:
            overlap_text = prev.content[-OVERLAP_CHARS:]
            # Find a word boundary for cleaner overlap
            space_idx = overlap_text.find(" ")
            if space_idx > 0:
                overlap_text = overlap_text[space_idx + 1:]

            result.append(Chunk(
                content=overlap_text + "... " + curr.content,
                file_path=curr.file_path,
                heading_path=curr.heading_path,
                line_start=curr.line_start,
                line_end=curr.line_end,
            ))
        else:
            result.append(curr)

    return result
