import json
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contracts import AskRequest, AskResponse, Expert, GapItem, Health, OnboardingPath, Stats
from app import config
from modules import ingestion, intelligence, retrieval

app = FastAPI(title='Provenance')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/ask', response_model=AskResponse)
def ask(req: AskRequest):
    start = time.time()
    resp = retrieval.answer(req.question, req.role)
    resp.latency_ms = int((time.time() - start) * 1000)
    return resp


@app.get('/onboarding', response_model=OnboardingPath)
def onboarding(job_role: str = 'QA', role: str = 'analyst'):
    return ingestion.onboarding_path(job_role, role)


@app.get('/experts', response_model=list[Expert])
def experts(topic: str = 'deviation', role: str = 'analyst'):
    return ingestion.find_experts(topic, role)


@app.get('/gaps', response_model=list[GapItem])
def gaps():
    return intelligence.gap_report()


@app.get('/stats', response_model=Stats)
def stats():
    return intelligence.get_stats()


@app.get('/health', response_model=Health)
def health():
    path = config.chunks_path()
    try:
        count = len(json.loads(path.read_text(encoding='utf-8')))
    except Exception:
        count = 0
    source = 'real' if path.name == 'chunks.json' else 'fixtures'
    return Health(status='ok', chunks=count, llm=config.llm_mode(), data_source=source)
