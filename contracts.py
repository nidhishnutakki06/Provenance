from pydantic import BaseModel
from typing import Literal, Optional

Role = Literal['intern', 'analyst', 'manager']
Source = Literal['sharepoint', 'sop', 'pdf', 'email', 'teams']

class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    source_type: Source
    title: str
    version: Optional[str] = None
    date: str                          # ISO yyyy-mm-dd
    author: str
    owner: Optional[str] = None
    status: Literal['current', 'superseded', 'draft'] = 'current'
    supersedes: Optional[str] = None   # doc_id it replaces
    allowed_roles: list[Role]
    location: str                      # 'page 3', 'section 2', 'msg 12-16'
    topics: list[str] = []

class Citation(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    source_type: Source
    version: Optional[str] = None
    date: str
    status: str
    snippet: str
    location: str

class Conflict(BaseModel):
    topic: str
    kind: Literal['contradiction', 'superseded'] = 'contradiction'
    explanation: str
    source_a: Citation
    source_b: Citation
    recommendation: str

class Expert(BaseModel):
    name: str
    role: str
    evidence_count: int
    topics: list[str]
    sample_source: str

class AskRequest(BaseModel):
    question: str
    role: Role

class AskResponse(BaseModel):
    answer: str
    answerable: bool
    confidence: Literal['high', 'medium', 'low']
    citations: list[Citation]
    conflicts: list[Conflict] = []
    missing_info: Optional[str] = None
    expanded_terms: dict[str, str] = {}
    experts: list[Expert] = []
    minutes_saved: float = 0.0
    latency_ms: int = 0

class ReadingItem(BaseModel):
    order: int
    doc_id: str
    title: str
    why: str
    est_minutes: int

class OnboardingPath(BaseModel):
    job_role: str
    days: dict[str, list[ReadingItem]]   # 'Day 1' .. 'Day 5'

class GapItem(BaseModel):
    question: str
    asked_count: int
    last_asked: str
    reason: str

class Stats(BaseModel):
    total_questions: int = 0
    answered: int = 0
    unanswered: int = 0
    total_minutes_saved: float = 0.0
    conflicts_flagged: int = 0
    by_role: dict[str, int] = {}

class Health(BaseModel):
    status: str = 'ok'
    chunks: int = 0
    llm: str = 'mock'            # mock | groq | offline
    data_source: str = 'fixtures'  # fixtures | real
