import json
from contracts import AskResponse, Chunk, Citation, Role
from app.config import chunks_path


def _load() -> list[Chunk]:
    return [Chunk(**c) for c in json.loads(chunks_path().read_text(encoding='utf-8'))]


def search(question: str, role: Role, k: int = 8) -> list[Chunk]:
    return [c for c in _load() if role in c.allowed_roles][:k]


def answer(question: str, role: Role) -> AskResponse:
    hits = search(question, role, 2)
    cites = [
        Citation(chunk_id=c.chunk_id, doc_id=c.doc_id, title=c.title, source_type=c.source_type,
                 version=c.version, date=c.date, status=c.status, snippet=c.text[:200], location=c.location)
        for c in hits
    ]
    text = '(stub) ' + hits[0].text + ' [1]' if hits else '(stub) No data.'
    return AskResponse(answer=text, answerable=bool(hits), confidence='low', citations=cites)
