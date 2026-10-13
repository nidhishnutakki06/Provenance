import json
import os
import sys
import tempfile
from pathlib import Path

# Ensure mock LLM for selftest
os.environ['USE_MOCK_LLM'] = '1'

from contracts import AskRequest, AskResponse, Chunk, Citation
from app import config
from modules.intelligence.conflicts import detect_conflicts
from modules.intelligence.gaps import gap_report, get_stats, log_query


def run_selftest() -> None:
    print("=== Running modules.intelligence.selftest ===")

    # -------------------------------------------------------------
    # Test 1: detect_conflicts on fixture chunks
    # -------------------------------------------------------------
    fixture_path = config.FIXTURES_DIR / 'chunks_sample.json'
    assert fixture_path.exists(), f"Fixture chunks file not found: {fixture_path}"

    raw_chunks = json.loads(fixture_path.read_text(encoding='utf-8'))
    chunks = [Chunk(**c) for c in raw_chunks]

    conflicts = detect_conflicts(chunks)
    print(f"[1] detect_conflicts returned {len(conflicts)} conflict(s):")
    for idx, c in enumerate(conflicts, 1):
        print(f"    Conflict {idx}: kind={c.kind}, topic='{c.topic}', "
              f"source_a={c.source_a.doc_id}, source_b={c.source_b.doc_id}")

    # Check contradiction conflict
    contradictions = [c for c in conflicts if c.kind == 'contradiction']
    assert len(contradictions) == 1, (
        f"Expected exactly 1 contradiction conflict, got {len(contradictions)}"
    )
    contra = contradictions[0]
    contra_docs = {contra.source_a.doc_id, contra.source_b.doc_id}
    assert 'SOP-014-v3' in contra_docs, (
        f"Contradiction should include SOP-014-v3, got {contra_docs}"
    )
    assert 'EML-001' in contra_docs or 'TEAMS-COLDCHAIN' in contra_docs, (
        f"Contradiction should include EML-001 or TEAMS-COLDCHAIN, got {contra_docs}"
    )
    assert contra.explanation, "Contradiction explanation must not be empty"
    assert contra.recommendation, "Contradiction recommendation must not be empty"
    print("    -> Contradiction check: PASS")

    # Check superseded conflict
    superseded = [c for c in conflicts if c.kind == 'superseded']
    assert len(superseded) == 1, (
        f"Expected exactly 1 superseded conflict, got {len(superseded)}"
    )
    super_conf = superseded[0]
    assert super_conf.source_a.doc_id == 'SOP-014-v2', (
        f"Superseded source_a should be SOP-014-v2, got {super_conf.source_a.doc_id}"
    )
    assert super_conf.source_b.doc_id == 'SOP-014-v3', (
        f"Superseded source_b should name newer doc SOP-014-v3, got {super_conf.source_b.doc_id}"
    )
    assert super_conf.explanation, "Superseded explanation must not be empty"
    assert super_conf.recommendation, "Superseded recommendation must not be empty"
    print("    -> Superseded check: PASS")

    # -------------------------------------------------------------
    # Test 2: log_query, gap_report, get_stats on a temp database
    # -------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_db = Path(tmpdir) / 'test_queries.sqlite'

        dummy_cit = Citation(
            chunk_id="SOP-001#001",
            doc_id="SOP-001",
            title="SOP-001 Deviation Handling",
            source_type="sop",
            version="1.0",
            date="2024-03-10",
            status="current",
            snippet="Report within 24 hours.",
            location="page 1",
        )

        # 1. Answered query
        req1 = AskRequest(question="How do I report a deviation?", role="analyst")
        resp1 = AskResponse(
            answer="Report within 24 hours. [1]",
            answerable=True,
            confidence="high",
            citations=[dummy_cit],
            conflicts=[],
            minutes_saved=9.0,
        )
        log_query(req1, resp1, db_path=temp_db)

        # 2. Unanswered HPLC query 1
        req2 = AskRequest(question="How do I calibrate an HPLC column?", role="analyst")
        resp2 = AskResponse(
            answer="No data.",
            answerable=False,
            confidence="low",
            citations=[],
            conflicts=[],
            missing_info="No source found for HPLC calibration",
        )
        log_query(req2, resp2, db_path=temp_db)

        # 3. Similar unanswered HPLC query 2
        req3 = AskRequest(question="How do I calibrate an HPLC column?", role="intern")
        resp3 = AskResponse(
            answer="No data.",
            answerable=False,
            confidence="low",
            citations=[],
            conflicts=[],
            missing_info="No source found for HPLC calibration",
        )
        log_query(req3, resp3, db_path=temp_db)

        # 4. Slightly reworded HPLC query 3 (Jaccard >= 0.6)
        req4 = AskRequest(question="How to calibrate HPLC column?", role="manager")
        resp4 = AskResponse(
            answer="No data.",
            answerable=False,
            confidence="low",
            citations=[],
            conflicts=[],
            missing_info="No source found for HPLC calibration",
        )
        log_query(req4, resp4, db_path=temp_db)

        # 5. Distinct unanswered query
        req5 = AskRequest(question="Where is the lunchroom located?", role="intern")
        resp5 = AskResponse(
            answer="No data.",
            answerable=False,
            confidence="low",
            citations=[],
            conflicts=[],
            missing_info="Facility map not found",
        )
        log_query(req5, resp5, db_path=temp_db)

        # Verify gap_report clustering
        gaps = gap_report(db_path=temp_db)
        print(f"[2] gap_report returned {len(gaps)} gap item(s):")
        for g in gaps:
            print(f"    Gap: '{g.question}', asked_count={g.asked_count}, "
                  f"last_asked={g.last_asked}, reason='{g.reason}'")

        assert len(gaps) == 2, f"Expected 2 clustered gaps, got {len(gaps)}"
        assert gaps[0].asked_count == 3, f"Expected HPLC cluster count 3, got {gaps[0].asked_count}"
        assert "hplc" in gaps[0].question.lower(), f"First gap should be HPLC question, got {gaps[0].question}"
        assert gaps[1].asked_count == 1, f"Second gap count should be 1, got {gaps[1].asked_count}"
        print("    -> gap_report clustering check: PASS")

        # Verify get_stats
        stats = get_stats(db_path=temp_db)
        print(f"[3] get_stats result: total={stats.total_questions}, "
              f"answered={stats.answered}, unanswered={stats.unanswered}, "
              f"minutes={stats.total_minutes_saved}, by_role={stats.by_role}")

        assert stats.total_questions == 5, f"Expected 5 total questions, got {stats.total_questions}"
        assert stats.answered == 1, f"Expected 1 answered, got {stats.answered}"
        assert stats.unanswered == 4, f"Expected 4 unanswered, got {stats.unanswered}"
        assert stats.total_minutes_saved == 9.0, f"Expected 9.0 minutes saved, got {stats.total_minutes_saved}"
        assert stats.by_role == {'analyst': 2, 'intern': 2, 'manager': 1}, (
            f"Unexpected role distribution: {stats.by_role}"
        )
        print("    -> get_stats check: PASS")

    print("\nALL SELFTESTS PASSED SUCCESSFULLY!")


if __name__ == '__main__':
    run_selftest()
