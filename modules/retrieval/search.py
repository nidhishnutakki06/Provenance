import sys
from typing import Optional

from contracts import Chunk, Role
from modules.retrieval.index import expand_query, get_role_index


def search_with_scores(question: str, role: Role, k: int = 8) -> list[tuple[float, Chunk]]:
    """
    Search chunks for a specific role with BM25 and glossary query expansion.
    Multiplies score of non-current chunks by 0.85.
    Returns list of (score, chunk) tuples sorted descending.
    """
    try:
        if not question or not question.strip():
            return []

        bm25, role_chunks = get_role_index(role)
        if not bm25 or not role_chunks:
            return []

        bm25_tokens, _ = expand_query(question)
        if not bm25_tokens:
            return []

        raw_scores = bm25.get_scores(bm25_tokens)

        scored: list[tuple[float, Chunk]] = []
        for idx, chunk in enumerate(role_chunks):
            score = float(raw_scores[idx])
            if chunk.status != 'current':
                score *= 0.85
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]
    except Exception as e:
        sys.stderr.write(f"[retrieval search error] {e}\n")
        return []


def search(question: str, role: Role, k: int = 8) -> list[Chunk]:
    """
    Public search API.
    Returns top k Chunk objects allowed for the given role.
    """
    results = search_with_scores(question, role, k=k)
    return [chunk for score, chunk in results]
