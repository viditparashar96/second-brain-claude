"""FastEmbed wrapper with markdown-aware chunking."""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from fastembed import TextEmbedding

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import MODEL_CACHE_DIR

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_CHUNK_CHARS = 400
OVERLAP_CHARS = 80

_model = None


def get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(MODEL_CACHE_DIR))
    return _model


def embed_texts(texts):
    return list(get_model().embed(texts, batch_size=256))


def embed_query(query):
    return list(get_model().embed([query]))[0]


@dataclass
class Chunk:
    content: str
    file_path: str
    heading_path: str
    line_start: int
    line_end: int


def chunk_markdown(file_path, text):
    lines = text.split("\n")
    sections = _split_by_headings(lines)
    chunks = []
    for heading_path, section_lines, start_line in sections:
        section_text = "\n".join(section_lines).strip()
        if not section_text:
            continue
        paragraphs = re.split(r"\n\s*\n", section_text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        section_chunks = _merge_paragraphs(paragraphs, file_path, heading_path, start_line)
        chunks.extend(section_chunks)
    return _add_overlap(chunks)


def _split_by_headings(lines):
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$")
    sections, current_headings = [], ["", "", ""]
    current_lines, current_start = [], 0
    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            if current_lines:
                path = " > ".join(h for h in current_headings if h)
                sections.append((path, current_lines, current_start))
            level = len(m.group(1)) - 1
            current_headings[level] = m.group(2).strip()
            for j in range(level + 1, 3):
                current_headings[j] = ""
            current_lines, current_start = [], i
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((" > ".join(h for h in current_headings if h), current_lines, current_start))
    return sections


def _merge_paragraphs(paragraphs, file_path, heading_path, base_line):
    chunks, current_text, chunk_start = [], "", base_line
    for para in paragraphs:
        if not current_text:
            current_text = para
            continue
        combined = current_text + "\n\n" + para
        if len(combined) <= MAX_CHUNK_CHARS:
            current_text = combined
        else:
            chunks.append(Chunk(current_text, file_path, heading_path, chunk_start, chunk_start + current_text.count("\n")))
            chunk_start += current_text.count("\n") + 2
            current_text = para
    if current_text:
        chunks.append(Chunk(current_text, file_path, heading_path, chunk_start, chunk_start + current_text.count("\n")))
    return chunks


def _add_overlap(chunks):
    if len(chunks) <= 1:
        return chunks
    result = [chunks[0]]
    for i in range(1, len(chunks)):
        prev, curr = chunks[i - 1], chunks[i]
        if prev.file_path == curr.file_path:
            overlap = prev.content[-OVERLAP_CHARS:]
            space = overlap.find(" ")
            if space > 0:
                overlap = overlap[space + 1:]
            result.append(Chunk(overlap + "... " + curr.content, curr.file_path, curr.heading_path, curr.line_start, curr.line_end))
        else:
            result.append(curr)
    return result
