import json
from pathlib import Path
import re
import sys
import time
from typing import Optional

from rank_bm25 import BM25Okapi

from app import config
from contracts import Chunk, Role

STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are',
    'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both',
    'but', 'by', 'can', 'cannot', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each',
    'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers',
    'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
    'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only',
    'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she',
    'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves',
    'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until',
    'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
    'why', 'with', 'would', 'you', 'your', 'yours', 'yourself', 'yourselves'
}

_GLOSSARY_CACHE: Optional[dict] = None
_GLOSSARY_PATH = Path(__file__).resolve().parent / 'glossary.json'

# Global cache for role BM25 indexes
_INDEX_CACHE: dict[Role, tuple[BM25Okapi, list[Chunk]]] = {}
_LAST_CHUNKS_PATH: Optional[Path] = None
_LAST_CHUNKS_MTIME: float = 0.0
_LAST_CHUNKS_SIZE: int = 0


def load_glossary() -> dict:
    global _GLOSSARY_CACHE
    if _GLOSSARY_CACHE is None:
        try:
            if _GLOSSARY_PATH.exists():
                _GLOSSARY_CACHE = json.loads(_GLOSSARY_PATH.read_text(encoding='utf-8'))
            else:
                _GLOSSARY_CACHE = {}
        except Exception as e:
            sys.stderr.write(f"[retrieval] Error loading glossary: {e}\n")
            _GLOSSARY_CACHE = {}
    return _GLOSSARY_CACHE


def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    """Tokenize by lowercasing and splitting on non-alphanumerics with a small stopword list."""
    if not text:
        return []
    tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


def find_expanded_terms(question: str) -> dict[str, str]:
    """Find glossary terms present in the question and map abbreviation to expansion."""
    glossary = load_glossary()
    found: dict[str, str] = {}
    q_lower = question.lower()

    for term, data in glossary.items():
        # Match as whole word case-insensitively
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        if re.search(pattern, q_lower):
            found[term] = data.get('expansion', '')

    return found


def expand_query(question: str) -> tuple[list[str], set[str]]:
    """
    Expand the query using the glossary.
    Returns:
      (bm25_query_tokens, distinctive_tokens)
    """
    glossary = load_glossary()
    q_tokens = tokenize(question, remove_stopwords=True)
    if not q_tokens:
        q_tokens = tokenize(question, remove_stopwords=False)

    bm25_tokens = list(q_tokens)
    distinctive_tokens = set(q_tokens)
    q_lower = question.lower()

    for term, data in glossary.items():
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        if re.search(pattern, q_lower):
            # Term directly matched in question
            exp_tokens = tokenize(data.get('expansion', ''))
            bm25_tokens.extend(exp_tokens)
            distinctive_tokens.update(exp_tokens)
            for also in data.get('also', []):
                bm25_tokens.extend(tokenize(also))
        else:
            # Check vocabulary bridging in 'also'
            for also in data.get('also', []):
                also_pattern = r'\b' + re.escape(also.lower()) + r'\b'
                if re.search(also_pattern, q_lower):
                    bm25_tokens.extend(tokenize(term))
                    break

    # Deduplicate while preserving order for BM25
    bm25_dedup = list(dict.fromkeys(bm25_tokens))
    return bm25_dedup, distinctive_tokens


def load_chunks() -> list[Chunk]:
    """Load chunks through app.config.chunks_path()."""
    path = config.chunks_path()
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding='utf-8'))
        return [Chunk(**item) for item in data]
    except Exception as e:
        sys.stderr.write(f"[retrieval] Error loading chunks from {path}: {e}\n")
        return []


def _ensure_indexes():
    global _INDEX_CACHE, _LAST_CHUNKS_PATH, _LAST_CHUNKS_MTIME, _LAST_CHUNKS_SIZE
    path = config.chunks_path()
    mtime = 0.0
    size = 0
    if path.exists():
        try:
            stat = path.stat()
            mtime = stat.st_mtime
            size = stat.st_size
        except Exception:
            pass

    # Check if rebuild is needed
    needs_rebuild = (
        not _INDEX_CACHE
        or path != _LAST_CHUNKS_PATH
        or mtime != _LAST_CHUNKS_MTIME
        or size != _LAST_CHUNKS_SIZE
    )

    if not needs_rebuild:
        return

    sys.stderr.write(f"[retrieval] Building BM25 role indexes from {path}\n")
    all_chunks = load_chunks()
    roles: list[Role] = ['intern', 'analyst', 'manager']
    new_cache: dict[Role, tuple[BM25Okapi, list[Chunk]]] = {}

    for r in roles:
        role_chunks = [c for c in all_chunks if r in c.allowed_roles]
        if role_chunks:
            corpus = [
                tokenize(f"{c.title} {c.text} {' '.join(c.topics)}")
                for c in role_chunks
            ]
            bm25 = BM25Okapi(corpus)
            new_cache[r] = (bm25, role_chunks)
        else:
            # Empty index
            new_cache[r] = (BM25Okapi([['']]), [])

    _INDEX_CACHE = new_cache
    _LAST_CHUNKS_PATH = path
    _LAST_CHUNKS_MTIME = mtime
    _LAST_CHUNKS_SIZE = size


def get_role_index(role: Role) -> tuple[Optional[BM25Okapi], list[Chunk]]:
    """Return the BM25 index and filtered chunks for the requested role."""
    _ensure_indexes()
    if role in _INDEX_CACHE:
        return _INDEX_CACHE[role]
    return None, []
