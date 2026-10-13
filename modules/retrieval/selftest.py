import os
import sys
import unittest.mock as mock

# Ensure USE_MOCK_LLM=1 is active for selftest
os.environ['USE_MOCK_LLM'] = '1'

from contracts import AskResponse, Chunk, Role
from modules.retrieval import answer, search
from modules.retrieval.search import search_with_scores


def run_selftest():
    print("=" * 60)
    print("Running modules.retrieval.selftest (USE_MOCK_LLM=1)")
    print("=" * 60)

    # 1. Assertion: An intern search never returns AUD-001 or EML-004 chunks
    print("\n[Test 1] Role security: Intern search never returns AUD-001 or EML-004 chunks...")
    intern_test_queries = [
        "What recurring deviation did the audit find?",
        "audit findings and internal review",
        "temperature excursion and audit prep",
        "Who knows about deviation handling?",
        "What temperature should vaccine batches be stored at?",
    ]
    for q in intern_test_queries:
        intern_chunks = search(q, role="intern", k=20)
        for c in intern_chunks:
            assert c.doc_id not in ["AUD-001", "EML-004"], (
                f"SECURITY VIOLATION: Intern received chunk {c.chunk_id} from restricted doc {c.doc_id}!"
            )
            assert "intern" in c.allowed_roles, (
                f"SECURITY VIOLATION: Intern received chunk {c.chunk_id} with allowed_roles={c.allowed_roles}!"
            )
    print("  -> PASS: All intern searches cleanly exclude restricted AUD-001 and EML-004.")

    # 2. Assertion: The vaccine storage question returns SOP-014-v3 chunks for an analyst
    print("\n[Test 2] Vaccine storage question returns SOP-014-v3 chunks for an analyst...")
    vaccine_q = "What temperature should vaccine batches be stored at?"
    analyst_chunks = search(vaccine_q, role="analyst", k=8)
    v3_chunks = [c for c in analyst_chunks if c.doc_id == "SOP-014-v3"]
    assert len(v3_chunks) > 0, (
        f"Expected SOP-014-v3 chunks for analyst vaccine storage query, got: {[c.doc_id for c in analyst_chunks]}"
    )
    assert any("2 to 8 °C" in c.text for c in v3_chunks), (
        "Expected SOP-014-v3 chunk to contain '2 to 8 °C' fixed sentence."
    )
    print(f"  -> PASS: Found {len(v3_chunks)} SOP-014-v3 chunks in analyst search results.")

    # 3. Assertion: The HPLC question and the intern audit question are answerable=false
    print("\n[Test 3] Answerability gate: HPLC question and intern audit question must be answerable=false...")
    hplc_q = "How do I calibrate an HPLC column?"
    resp_hplc = answer(hplc_q, role="analyst")
    assert resp_hplc.answerable is False, f"HPLC question should be answerable=False, got {resp_hplc.answerable}"
    assert resp_hplc.confidence == "low", f"HPLC confidence should be 'low', got {resp_hplc.confidence}"
    assert len(resp_hplc.citations) == 0, f"HPLC should have 0 citations, got {len(resp_hplc.citations)}"
    assert resp_hplc.missing_info is not None, "HPLC should include missing_info"
    assert "restricted" not in (resp_hplc.missing_info or "").lower(), "Refusal must not mention restricted docs"
    print("  -> PASS: HPLC question returned answerable=False, confidence=low, citations=[].")

    audit_q = "What recurring deviation did the audit find?"
    resp_intern_audit = answer(audit_q, role="intern")
    assert resp_intern_audit.answerable is False, (
        f"Intern audit question should be answerable=False, got {resp_intern_audit.answerable}"
    )
    assert resp_intern_audit.confidence == "low", f"Intern audit confidence should be 'low', got {resp_intern_audit.confidence}"
    assert len(resp_intern_audit.citations) == 0, f"Intern audit should have 0 citations, got {len(resp_intern_audit.citations)}"
    assert resp_intern_audit.missing_info is not None, "Intern audit should include missing_info"
    assert "restricted" not in (resp_intern_audit.missing_info or "").lower(), "Refusal must not mention restricted docs"
    assert "aud-001" not in (resp_intern_audit.missing_info or "").lower(), "Refusal must never leak doc_id AUD-001"
    print("  -> PASS: Intern audit question returned answerable=False with no leaked documents.")

    # 4. Assertion: The OOS question returns expanded_terms with CAPA and OOS
    print("\n[Test 4] Glossary expansion: OOS question returns expanded_terms with CAPA and OOS...")
    oos_q = "What is the CAPA timeline for an OOS result?"
    resp_oos = answer(oos_q, role="analyst")
    assert "CAPA" in resp_oos.expanded_terms, f"Expected 'CAPA' in expanded_terms, got: {resp_oos.expanded_terms}"
    assert "OOS" in resp_oos.expanded_terms, f"Expected 'OOS' in expanded_terms, got: {resp_oos.expanded_terms}"
    assert "Corrective and Preventive Action" in resp_oos.expanded_terms["CAPA"]
    assert "Out of Specification" in resp_oos.expanded_terms["OOS"]
    print(f"  -> PASS: expanded_terms contains: {resp_oos.expanded_terms}")

    # 5. Assertion: The extractive path returns at least one citation
    print("\n[Test 5] Extractive fallback path returns at least one citation (under USE_MOCK_LLM=1)...")
    resp_extractive = answer(vaccine_q, role="analyst")
    assert resp_extractive.answerable is True, "Expected answerable=True on extractive path"
    assert len(resp_extractive.citations) >= 1, (
        f"Expected at least 1 citation on extractive path, got {len(resp_extractive.citations)}"
    )
    assert "[1]" in resp_extractive.answer, "Expected [1] citation marker in extractive answer text"
    assert resp_extractive.confidence in ["medium", "low"], (
        f"Expected medium/low confidence, got {resp_extractive.confidence}"
    )
    for c in resp_extractive.citations:
        assert c.snippet and len(c.snippet.strip()) > 0, f"Citation snippet must not be empty: {c}"
        assert len(c.snippet.split()) <= 45, f"Citation snippet should be ~40 words, got: {len(c.snippet.split())}"
    print(f"  -> PASS: Extractive path returned {len(resp_extractive.citations)} citations with valid snippets.")

    # 6. Assertion: LLM JSON response path with renumbering and non-current confidence
    print("\n[Test 6] LLM response mapping, renumbering, and non-current confidence check...")
    # 6a: Test renumbering
    mock_json_ok = {
        'answer': 'Per SOP-014 [2], store at 2 to 8 °C. Per QA email [1], store at 2 to 6 °C.',
        'answerable': True,
        'confidence': 'high',
        'used_passages': [2, 1],
        'missing_info': None
    }
    with mock.patch('app.llm.complete_json', return_value=mock_json_ok):
        resp_llm = answer(vaccine_q, role='analyst')
        assert resp_llm.answerable is True
        assert len(resp_llm.citations) == 2
        assert '[1]' in resp_llm.answer and '[2]' in resp_llm.answer
    print("  -> PASS: Citation markers successfully renumbered to match citation order.")

    # 6b: Test confidence low when all cited chunks are non-current
    hits = search_with_scores("What happens if a temperature excursion occurs in cold storage?", role="analyst", k=8)
    superseded_indices = [i + 1 for i, (s, c) in enumerate(hits) if c.status == "superseded"]
    assert len(superseded_indices) > 0, "Expected at least one superseded chunk in excursion results"
    v2_idx = superseded_indices[0]

    mock_json_superseded = {
        'answer': f'Excursions of up to 12 hours do not require a deviation report [{v2_idx}].',
        'answerable': True,
        'confidence': 'high',
        'used_passages': [v2_idx],
        'missing_info': None
    }
    with mock.patch('app.llm.complete_json', return_value=mock_json_superseded):
        resp_sup = answer("What happens if a temperature excursion occurs in cold storage?", role="analyst")
        assert resp_sup.citations[0].status == "superseded"
        assert resp_sup.confidence == "low", f"Expected confidence 'low' when citing only superseded chunk, got {resp_sup.confidence}"
        assert "[1]" in resp_sup.answer
    print("  -> PASS: Confidence downgraded to 'low' when all cited chunks are non-current.")

    # 7. Additional verification: 12 golden questions behavior check
    print("\n[Test 7] 12 Golden questions behavior validation...")
    golden_expectations = [
        ("G1", "What temperature should vaccine batches be stored at?", "analyst", True),
        ("G2", "What temperature should vaccine batches be stored at?", "intern", True),
        ("G3", "What temperature should vaccine batches be stored at?", "manager", True),
        ("G4", "What is the CAPA timeline for an OOS result?", "analyst", True),
        ("G5", "What is the CAPA timeline for an OOS result?", "intern", False),
        ("G6", "What recurring deviation did the audit find?", "intern", False),
        ("G7", "What recurring deviation did the audit find?", "manager", True),
        ("G8", "How do I calibrate an HPLC column?", "analyst", False),
        ("G9", "Who knows about deviation handling?", "analyst", True),
        ("G10", "How do I report a deviation?", "intern", True),
        ("G11", "What should I read in my first week as a new QA hire?", "analyst", True),
        ("G12", "What happens if a temperature excursion occurs in cold storage?", "analyst", True),
    ]

    for gid, q, role, expected_answerable in golden_expectations:
        resp = answer(q, role=role)
        assert resp.answerable == expected_answerable, (
            f"Golden question {gid} ({role}) expected answerable={expected_answerable}, got {resp.answerable}"
        )
        if not expected_answerable:
            assert len(resp.citations) == 0, f"{gid} should have 0 citations on refusal"
            assert resp.confidence == "low", f"{gid} confidence should be low on refusal"
        else:
            assert len(resp.citations) >= 1, f"{gid} should have >=1 citations when answerable"
        print(f"  -> {gid} ({role:7s}): answerable={str(resp.answerable):5s}, citations={len(resp.citations)}, confidence={resp.confidence}")

    # 8. Regression assertion: G6 intern audit query on real corpus
    print("\n[Test 8] Regression: G6 intern audit refusal on real corpus (chunks.json)...")
    from app import config
    chunks_file = config.chunks_path()
    if chunks_file.name == 'chunks.json':
        resp_g6 = answer("What recurring deviation did the audit find?", role="intern")
        assert resp_g6.answerable is False, (
            f"Regression failed: Intern audit question on real corpus should be answerable=False, got {resp_g6.answerable}"
        )
        assert len(resp_g6.citations) == 0, (
            f"Regression failed: Intern audit question on real corpus should have 0 citations, got {len(resp_g6.citations)}"
        )
        assert resp_g6.confidence == "low", (
            f"Regression failed: Intern audit question confidence should be 'low', got {resp_g6.confidence}"
        )
        print("  -> PASS: G6 intern audit question cleanly refused with no citations on real corpus.")
    else:
        print(f"  -> SKIPPED: Real chunks.json not present (currently using {chunks_file.name}).")

    print("\n" + "=" * 60)
    print("ALL RETRIEVAL SELFTESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_selftest()
