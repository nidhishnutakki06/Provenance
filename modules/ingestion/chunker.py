"""Text chunking utilities for Provenance documents.

Splits document text into chunks of approximately 150 words with 20 words of overlap.
Supports stable chunk IDs formatted as <doc_id>#001, <doc_id>#002, etc.
"""

from __future__ import annotations


def split_words_with_overlap(text: str, chunk_size: int = 150, overlap: int = 20) -> list[str]:
    """Split text into chunks of approximately chunk_size words with overlap words."""
    words = text.split()
    if not words:
        return []
    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    i = 0
    while i < len(words):
        window = words[i : i + chunk_size]
        if window:
            chunks.append(" ".join(window))
        if i + chunk_size >= len(words):
            break
        i += step

    return chunks


def make_chunk_id(doc_id: str, index: int) -> str:
    """Generate a stable chunk_id formatted as <doc_id>#001."""
    return f"{doc_id}#{index:03d}"
