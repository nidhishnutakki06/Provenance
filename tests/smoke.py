import json
import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Run smoke test with mock LLM by default
os.environ.setdefault('USE_MOCK_LLM', '1')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

FALLBACK_GOLDEN_QUESTIONS = [
    {"id": "G1", "question": "What temperature should vaccine batches be stored at?", "role": "analyst"},
    {"id": "G2", "question": "What temperature should vaccine batches be stored at?", "role": "intern"},
    {"id": "G3", "question": "What temperature should vaccine batches be stored at?", "role": "manager"},
    {"id": "G4", "question": "What is the CAPA timeline for an OOS result?", "role": "analyst"},
    {"id": "G5", "question": "What is the CAPA timeline for an OOS result?", "role": "intern"},
    {"id": "G6", "question": "What recurring deviation did the audit find?", "role": "intern"},
    {"id": "G7", "question": "What recurring deviation did the audit find?", "role": "manager"},
    {"id": "G8", "question": "How do I calibrate an HPLC column?", "role": "analyst"},
    {"id": "G9", "question": "Who knows about deviation handling?", "role": "analyst"},
    {"id": "G10", "question": "How do I report a deviation?", "role": "intern"},
    {"id": "G11", "question": "What should I read in my first week as a new QA hire?", "role": "analyst"},
    {"id": "G12", "question": "What happens if a temperature excursion occurs in cold storage?", "role": "analyst"},
]


def load_golden_questions() -> list[dict]:
    golden_path = ROOT_DIR / 'corpus_gen' / 'golden_questions.json'
    if golden_path.exists():
        try:
            return json.loads(golden_path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"Notice: Failed to read golden_questions.json ({e}), using fallback.", file=sys.stderr)
    return FALLBACK_GOLDEN_QUESTIONS


def run_smoke_tests() -> None:
    print("=== Running Provenance Smoke Tests ===")

    # -------------------------------------------------------------
    # 1. Call every endpoint for all 3 roles
    # -------------------------------------------------------------
    roles = ['intern', 'analyst', 'manager']

    # Health
    r_health = client.get('/health')
    assert r_health.status_code == 200, f"/health returned {r_health.status_code}"
    health_data = r_health.json()
    assert health_data.get('status') == 'ok', f"Unexpected health status: {health_data}"
    print(f"[1] /health OK: chunks={health_data.get('chunks')}, data_source={health_data.get('data_source')}")

    # Stats & Gaps
    r_stats = client.get('/stats')
    assert r_stats.status_code == 200, f"/stats returned {r_stats.status_code}"

    r_gaps = client.get('/gaps')
    assert r_gaps.status_code == 200, f"/gaps returned {r_gaps.status_code}"
    print("[2] /stats and /gaps OK")

    # Role-based calls: /ask, /onboarding, /experts
    for role in roles:
        r_ask = client.post('/ask', json={'question': 'How do I report a deviation?', 'role': role})
        assert r_ask.status_code == 200, f"/ask for {role} failed with {r_ask.status_code}"
        ask_data = r_ask.json()
        assert 'answer' in ask_data and 'answerable' in ask_data

        r_onb = client.get(f'/onboarding?job_role=QA&role={role}')
        assert r_onb.status_code == 200, f"/onboarding for {role} failed with {r_onb.status_code}"

        r_exp = client.get(f'/experts?topic=deviation&role={role}')
        assert r_exp.status_code == 200, f"/experts for {role} failed with {r_exp.status_code}"

    print("[3] All endpoints called successfully for intern, analyst, and manager")

    # -------------------------------------------------------------
    # 2. Assert an intern never receives a citation or conflict source
    #    from AUD-001 or EML-004 for any question in the golden set
    # -------------------------------------------------------------
    golden_questions = load_golden_questions()
    restricted_docs = {'AUD-001', 'EML-004'}

    for item in golden_questions:
        q = item['question']
        resp = client.post('/ask', json={'question': q, 'role': 'intern'})
        assert resp.status_code == 200, f"/ask failed for intern on question '{q}'"
        data = resp.json()

        # Check citations
        for cit in data.get('citations', []):
            doc_id = cit.get('doc_id')
            assert doc_id not in restricted_docs, (
                f"SECURITY VIOLATION: Intern received restricted citation '{doc_id}' for question: {q}"
            )

        # Check conflict sources
        for conf in data.get('conflicts', []):
            doc_a = conf.get('source_a', {}).get('doc_id')
            doc_b = conf.get('source_b', {}).get('doc_id')
            assert doc_a not in restricted_docs and doc_b not in restricted_docs, (
                f"SECURITY VIOLATION: Intern received conflict referencing restricted document "
                f"('{doc_a}', '{doc_b}') for question: {q}"
            )

    print(f"[4] PASS: Intern never receives AUD-001 or EML-004 across {len(golden_questions)} golden questions")

    # -------------------------------------------------------------
    # 3. Assert analyst vaccine-storage question returns at least one conflict
    #    (run only when /health data_source is real, otherwise print SKIPPED)
    # -------------------------------------------------------------
    if health_data.get('data_source') == 'real':
        resp_vaccine = client.post(
            '/ask',
            json={'question': 'What temperature should vaccine batches be stored at?', 'role': 'analyst'}
        )
        assert resp_vaccine.status_code == 200
        vaccine_data = resp_vaccine.json()
        assert len(vaccine_data.get('conflicts', [])) >= 1, (
            f"Expected at least 1 conflict for vaccine question on real data, got {len(vaccine_data.get('conflicts', []))}"
        )
        print("[5] PASS: Analyst vaccine-storage question returned conflict(s)")
    else:
        print("[5] SKIPPED: vaccine-storage conflict assertion requires real data_source")

    # -------------------------------------------------------------
    # 4. Assert unanswerable responses have no citations
    # -------------------------------------------------------------
    hplc_resp = client.post(
        '/ask',
        json={'question': 'How do I calibrate an HPLC column?', 'role': 'analyst'}
    )
    assert hplc_resp.status_code == 200
    hplc_data = hplc_resp.json()
    if not hplc_data.get('answerable'):
        assert len(hplc_data.get('citations', [])) == 0, (
            f"Unanswerable response had citations: {hplc_data.get('citations')}"
        )

    # Check across all responses collected: any unanswerable response must have citations == []
    for item in golden_questions:
        for r in roles:
            check_resp = client.post('/ask', json={'question': item['question'], 'role': r})
            if check_resp.status_code == 200:
                c_data = check_resp.json()
                if not c_data.get('answerable'):
                    assert len(c_data.get('citations', [])) == 0, (
                        f"Unanswerable response for question '{item['question']}' (role={r}) contained citations!"
                    )

    print("[6] PASS: Unanswerable responses strictly have no citations")

    print("\nALL SMOKE TESTS PASSED!")


if __name__ == '__main__':
    run_smoke_tests()
