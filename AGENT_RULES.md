Project: Provenance, a trust-first enterprise knowledge assistant (pharma, fictional company Novacure Labs).
Build window: 3 hours. Simple and working beats clever.
Read PLAN.md first, especially sections 2 (ownership), 3 (APIs), 5 (contracts) and 6 (corpus).

Rules:
1. Never edit contracts.py or app/config.py. If a change seems needed, stop and tell the human.
2. Only create or edit files inside the paths you own (PLAN.md section 2). Never touch another dev's files.
3. Every public function must match the signature in PLAN.md section 5.2 exactly, and be exported from your package __init__.py (replace the stub).
4. Functions never raise on bad input. Return an empty or safe result and log the error to stderr.
5. Everything must be free and local. LLM calls only through app/llm.py (corpus_gen/client.py is the one exception).
6. Never hardcode secrets or model names. Read GROQ_API_KEY, GROQ_MODEL_MAIN, GROQ_MODEL_FAST, USE_MOCK_LLM from the environment.
7. Do not call the LLM during ingestion, indexing, search, gap reporting or server startup.
8. Security: filter chunks by role BEFORE ranking and before any text reaches the LLM. A refusal must never reveal that a restricted document exists.
9. Get all file paths from app/config.py. Never build your own paths.
10. Add a selftest runnable as python -m <your.module>.selftest that uses fixtures and needs no network and no API key.
11. Keep code short, commented and dependency-light. Do not add packages.
12. Use the exact doc_ids, fixed sentences and topic vocabulary from PLAN.md sections 5.5 and 6.
13. Commit only to your own branch. Never push to main.
14. Before finishing, run your selftest, fix failures, then summarize what works and what does not.
