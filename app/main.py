import json
import sys
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contracts import (
    AskRequest,
    AskResponse,
    Expert,
    GapItem,
    Health,
    OnboardingPath,
    Stats,
)
from app import config
from modules import ingestion, intelligence, retrieval

app = FastAPI(title='Provenance')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

TOPIC_KEYWORDS = {
    'deviation': 'deviation',
    'deviations': 'deviation',
    'capa': 'capa',
    'oos': 'oos',
    'out of specification': 'oos',
    'cold-chain': 'cold-chain',
    'cold chain': 'cold-chain',
    'cold storage': 'cold-chain',
    'vaccine': 'cold-chain',
    'storage-temperature': 'storage-temperature',
    'storage temperature': 'storage-temperature',
    'temperature': 'storage-temperature',
    'excursion': 'cold-chain',
    'audit': 'audit',
    'auditing': 'audit',
    'onboarding': 'onboarding',
    'new hire': 'onboarding',
    'first week': 'onboarding',
    'new-joiner': 'new-joiner',
    'new joiner': 'new-joiner',
    'data-integrity': 'data-integrity',
    'data integrity': 'data-integrity',
    'alcoa': 'data-integrity',
    'stability': 'stability',
    'equipment': 'equipment',
    'regulatory': 'regulatory',
    'quality-system': 'quality-system',
    'quality system': 'quality-system',
}


def _extract_topic(question: str) -> str:
    q_lower = question.lower()
    for kw, topic in TOPIC_KEYWORDS.items():
        if kw in q_lower:
            return topic
    return ""


@app.post('/ask', response_model=AskResponse)
def ask(req: AskRequest):
    start = time.time()
    try:
        chunks = retrieval.search(req.question, req.role)
        resp = retrieval.answer(req.question, req.role)

        if resp.answerable:
            resp.conflicts = intelligence.detect_conflicts(chunks)
            topic = _extract_topic(req.question)
            if topic:
                try:
                    resp.experts = ingestion.find_experts(topic, req.role)
                except Exception as e:
                    print(f"Error finding experts: {e}", file=sys.stderr)
                    resp.experts = []
            else:
                resp.experts = []

            distinct_source_types = len({c.source_type for c in resp.citations})
            resp.minutes_saved = round(6.0 * (1.0 + 0.5 * distinct_source_types), 1)
        else:
            resp.conflicts = []
            resp.experts = []
            resp.citations = []
            resp.minutes_saved = 0.0

        resp.latency_ms = int((time.time() - start) * 1000)

        # RE-CHECK ROLES:
        # Load chunk_id to allowed_roles from app.config.chunks_path()
        # and drop any citation or conflict source the role may not see.
        try:
            chunks_path = config.chunks_path()
            if chunks_path.exists():
                raw_chunks = json.loads(chunks_path.read_text(encoding='utf-8'))
                chunk_allowed = {
                    c.get('chunk_id'): c.get('allowed_roles', [])
                    for c in raw_chunks
                }
                doc_allowed = {
                    c.get('doc_id'): c.get('allowed_roles', [])
                    for c in raw_chunks
                }
            else:
                chunk_allowed = {}
                doc_allowed = {}
        except Exception as e:
            print(f"Error loading chunks for role validation: {e}", file=sys.stderr)
            chunk_allowed = {}
            doc_allowed = {}

        if chunk_allowed or doc_allowed:
            # Filter citations
            filtered_cites = []
            for cit in resp.citations:
                allowed = chunk_allowed.get(cit.chunk_id) or doc_allowed.get(cit.doc_id)
                if allowed is None or req.role in allowed:
                    filtered_cites.append(cit)
            resp.citations = filtered_cites

            # Filter conflicts
            filtered_conflicts = []
            for conf in resp.conflicts:
                allowed_a = chunk_allowed.get(conf.source_a.chunk_id) or doc_allowed.get(conf.source_a.doc_id)
                allowed_b = chunk_allowed.get(conf.source_b.chunk_id) or doc_allowed.get(conf.source_b.doc_id)
                ok_a = allowed_a is None or req.role in allowed_a
                ok_b = allowed_b is None or req.role in allowed_b
                if ok_a and ok_b:
                    filtered_conflicts.append(conf)
            resp.conflicts = filtered_conflicts

        # If answerable but citations were stripped by role re-check, refuse safely
        if resp.answerable and not resp.citations:
            resp.answerable = False
            resp.confidence = 'low'
            resp.citations = []
            resp.conflicts = []
            resp.missing_info = "I do not have access to sufficient information to answer this question."
            resp.answer = "I do not have access to sufficient information to answer this question."
            resp.minutes_saved = 0.0

        if not resp.answerable:
            resp.citations = []
            resp.conflicts = []
            resp.minutes_saved = 0.0

        intelligence.log_query(req, resp)
        return resp

    except Exception as e:
        print(f"Error handling /ask: {e}", file=sys.stderr)
        safe_resp = AskResponse(
            answer="Something went wrong, please try again.",
            answerable=False,
            confidence="low",
            citations=[],
            conflicts=[],
            missing_info="Something went wrong, please try again.",
            latency_ms=int((time.time() - start) * 1000)
        )
        intelligence.log_query(req, safe_resp)
        return safe_resp


@app.get('/onboarding', response_model=OnboardingPath)
def onboarding(job_role: str = 'QA', role: str = 'analyst'):
    try:
        return ingestion.onboarding_path(job_role, role)
    except Exception as e:
        print(f"Error in /onboarding: {e}", file=sys.stderr)
        return OnboardingPath(job_role=job_role, days={})


@app.get('/experts', response_model=list[Expert])
def experts(topic: str = 'deviation', role: str = 'analyst'):
    try:
        return ingestion.find_experts(topic, role)
    except Exception as e:
        print(f"Error in /experts: {e}", file=sys.stderr)
        return []


@app.get('/gaps', response_model=list[GapItem])
def gaps():
    try:
        return intelligence.gap_report()
    except Exception as e:
        print(f"Error in /gaps: {e}", file=sys.stderr)
        return []


@app.get('/stats', response_model=Stats)
def stats():
    try:
        return intelligence.get_stats()
    except Exception as e:
        print(f"Error in /stats: {e}", file=sys.stderr)
        return Stats()


@app.get('/health', response_model=Health)
def health():
    path = config.chunks_path()
    try:
        count = len(json.loads(path.read_text(encoding='utf-8')))
    except Exception:
        count = 0
    source = 'real' if path.name == 'chunks.json' else 'fixtures'
    return Health(status='ok', chunks=count, llm=config.llm_mode(), data_source=source)
