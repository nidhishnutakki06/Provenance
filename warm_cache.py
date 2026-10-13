import json
import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Use mock LLM or environment mode
os.environ.setdefault('USE_MOCK_LLM', '1')

from fastapi.testclient import TestClient
from app.main import app

GOLDEN_QUESTIONS_PATH = ROOT_DIR / 'corpus_gen' / 'golden_questions.json'


def evaluate_behavior(expected_behavior: str, answerable: bool, n_citations: int, n_conflicts: int) -> bool:
    expected = expected_behavior.lower()
    if 'conflict' in expected:
        return n_conflicts > 0
    elif 'refuse' in expected or 'unanswerable' in expected:
        return not answerable and n_citations == 0
    elif 'answer' in expected:
        return answerable and n_citations > 0
    return answerable


def run_warm_cache() -> None:
    if not GOLDEN_QUESTIONS_PATH.exists():
        print(f"Warning: {GOLDEN_QUESTIONS_PATH} is missing, skipping warm_cache.", file=sys.stderr)
        return

    try:
        golden_data = json.loads(GOLDEN_QUESTIONS_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Warning: Failed to load {GOLDEN_QUESTIONS_PATH}: {e}", file=sys.stderr)
        return

    client = TestClient(app)
    roles = ['intern', 'analyst', 'manager']

    print("=== Provenance Cache Warming & Golden Evaluation ===")
    header = f"{'ID':<4} | {'Role':<8} | {'Answerable':<10} | {'Confidence':<10} | {'Citations':<9} | {'Conflicts':<9} | {'Result':<6} | Question"
    print(header)
    print("-" * 105)

    passed = 0
    failed = 0
    total_evals = 0

    for item in golden_data:
        qid = item.get('id', '')
        question = item.get('question', '')
        target_role = item.get('role', '')
        expected_behavior = item.get('expected_behavior', 'answer')

        for role in roles:
            resp = client.post('/ask', json={'question': question, 'role': role})
            if resp.status_code != 200:
                print(f"{qid:<4} | {role:<8} | {'ERROR':<10} | {'-':<10} | {'-':<9} | {'-':<9} | {'FAIL':<6} | {question[:40]}")
                if role == target_role:
                    failed += 1
                    total_evals += 1
                continue

            data = resp.json()
            answerable = bool(data.get('answerable', False))
            confidence = str(data.get('confidence', 'low'))
            n_citations = len(data.get('citations', []))
            n_conflicts = len(data.get('conflicts', []))

            if role == target_role:
                is_pass = evaluate_behavior(expected_behavior, answerable, n_citations, n_conflicts)
                result_str = "PASS" if is_pass else "FAIL"
                total_evals += 1
                if is_pass:
                    passed += 1
                else:
                    failed += 1
            else:
                result_str = "-"

            print(
                f"{qid:<4} | {role:<8} | {str(answerable):<10} | {confidence:<10} | "
                f"{n_citations:<9} | {n_conflicts:<9} | {result_str:<6} | {question[:40]}"
            )

    print("-" * 105)
    print(f"Evaluation Summary: {passed}/{total_evals} target-role checks passed ({failed} failed).")


if __name__ == '__main__':
    run_warm_cache()
