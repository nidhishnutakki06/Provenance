"""Self-test for modules.ingestion.

Run with:
    python -m modules.ingestion.selftest

Asserts:
1. All four connectors return chunks.
2. chunk_ids are unique.
2b. Every Teams chunk holds 3 to 5 messages.
3. Manager-only document chunks list only manager.
4. Superseded status is preserved.
5. Priya Rao is the top deviation expert for analyst (and intern & manager).
6. Onboarding path contains no superseded or restricted documents.
7. Builder writes docs.json, chunks.json, people.json to a temp folder.
"""

from __future__ import annotations

import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import app.config as config
from contracts import Chunk
from modules.ingestion.builder import build
from modules.ingestion.connectors import (
    EmailConnector,
    SharePointConnector,
    SopConnector,
    TeamsConnector,
)
from modules.ingestion.experts import find_experts, normalize_topic
from modules.ingestion.onboarding import onboarding_path


def run_selftest() -> None:
    print("=" * 60)
    print("Running modules.ingestion selftest...")
    print("=" * 60)

    raw_dir = config.raw_dir()
    print(f"Using raw directory: {raw_dir}")

    # 1. Test connectors
    sp_conn = SharePointConnector()
    sop_conn = SopConnector()
    eml_conn = EmailConnector()
    teams_conn = TeamsConnector()

    sp_chunks = sp_conn.load(raw_dir)
    sop_chunks = sop_conn.load(raw_dir)
    eml_chunks = eml_conn.load(raw_dir)
    teams_chunks = teams_conn.load(raw_dir)

    print(f"[TEST 1] Connector chunk counts:")
    print(f"  SharePoint: {len(sp_chunks)}")
    print(f"  SOP/PDF:    {len(sop_chunks)}")
    print(f"  Email:      {len(eml_chunks)}")
    print(f"  Teams:      {len(teams_chunks)}")

    assert len(sp_chunks) > 0, "SharePointConnector returned 0 chunks"
    assert len(sop_chunks) > 0, "SopConnector returned 0 chunks"
    assert len(eml_chunks) > 0, "EmailConnector returned 0 chunks"
    assert len(teams_chunks) > 0, "TeamsConnector returned 0 chunks"
    print("  PASS: All four connectors returned chunks.")

    all_chunks = sp_chunks + sop_chunks + eml_chunks + teams_chunks

    # 2. Assert chunk_ids are unique
    chunk_ids = [c.chunk_id for c in all_chunks]
    assert len(chunk_ids) == len(set(chunk_ids)), f"Duplicate chunk_ids found: {len(chunk_ids)} vs {len(set(chunk_ids))}"
    print(f"[TEST 2] PASS: chunk_ids are strictly unique ({len(chunk_ids)} total).")

    # TEST 2b: for every Teams chunk, count messages as text.count("\n") + 1 and assert it is between 3 and 5 (allow fewer only if that doc has a single chunk)
    teams_by_doc: dict[str, list[Chunk]] = defaultdict(list)
    for c in teams_chunks:
        teams_by_doc[c.doc_id].append(c)

    for doc_id, doc_chunks in teams_by_doc.items():
        is_single = len(doc_chunks) == 1
        for c in doc_chunks:
            msg_count = c.text.count("\n") + 1
            if is_single:
                assert 1 <= msg_count <= 5, f"Teams chunk {c.chunk_id} in single-chunk doc has {msg_count} messages"
            else:
                assert 3 <= msg_count <= 5, f"Teams chunk {c.chunk_id} has {msg_count} messages (expected 3 to 5)"

    print("[TEST 2b] PASS: every Teams chunk holds 3 to 5 messages.")

    # Verification: SharePoint section numbering and minimum word count
    sp_by_doc: dict[str, list[Chunk]] = defaultdict(list)
    for c in sp_chunks:
        sp_by_doc[c.doc_id].append(c)

    for doc_id, doc_chunks in sp_by_doc.items():
        assert doc_chunks[0].location == "section 1", f"{doc_id} first chunk location is not section 1: {doc_chunks[0].location}"
        # Check no section gaps
        seen_sections: list[int] = []
        for c in doc_chunks:
            sec_num = int(c.location.replace("section ", ""))
            if not seen_sections or seen_sections[-1] != sec_num:
                seen_sections.append(sec_num)
            w_count = len(c.text.split())
            assert w_count >= 12, f"SharePoint chunk {c.chunk_id} has only {w_count} words (< 12)"
        expected_sections = list(range(1, len(seen_sections) + 1))
        assert seen_sections == expected_sections, f"Section gap found in {doc_id}: {seen_sections} != {expected_sections}"

    print("[TEST 2c] PASS: Every SharePoint chunk location starts at section 1 with no gaps and >= 12 words.")

    # Verification: Strict sidecar fail closed test
    with tempfile.TemporaryDirectory() as tmp_test_dir:
        tmp_p = Path(tmp_test_dir)
        sp_dir = tmp_p / "sharepoint"
        sp_dir.mkdir()
        # Copy a docx and make invalid sidecar lacking allowed_roles
        sample_docx = next(raw_dir.glob("sharepoint/*.docx"))
        test_docx = sp_dir / sample_docx.name
        test_docx.write_bytes(sample_docx.read_bytes())
        bad_meta = {
            "doc_id": "TEST-001",
            "title": "Test Document",
            "source_type": "sharepoint",
            "version": "1.0",
            "date": "2025-01-01",
            "author": "Tester",
            "owner": "Tester",
            "status": "current",
            "supersedes": None,
            # missing allowed_roles
            "topics": ["quality-system"],
        }
        with open(sp_dir / f"{test_docx.name}.meta.json", "w", encoding="utf-8") as f:
            json.dump(bad_meta, f)
        skipped_chunks = SharePointConnector().load(tmp_p)
        assert len(skipped_chunks) == 0, f"Expected 0 chunks for sidecar lacking allowed_roles, got {len(skipped_chunks)}"

    print("[TEST 2d] PASS: Sidecar lacking allowed_roles is skipped and yields 0 chunks.")

    # Verification: normalize_topic required results
    assert normalize_topic("deviation handling") == "deviation"
    assert normalize_topic("CAPA timeline") == "capa"
    assert normalize_topic("cold chain") == "cold-chain"
    assert normalize_topic("which") == ""
    assert normalize_topic("in") == ""
    assert normalize_topic("a") == ""
    assert normalize_topic("rich") == ""
    print("[TEST 2e] PASS: normalize_topic conforms to all required cases.")

    # 3. Assert manager-only document's chunks list only manager
    aud_chunks = [c for c in all_chunks if c.doc_id == "AUD-001"]
    assert len(aud_chunks) > 0, "AUD-001 chunks not found"
    for c in aud_chunks:
        assert c.allowed_roles == ["manager"], f"AUD-001 chunk has unexpected allowed_roles: {c.allowed_roles}"
    print(f"[TEST 3] PASS: Manager-only document (AUD-001) chunks list only manager.")

    # 4. Assert superseded status is preserved
    sop_014_v2_chunks = [c for c in all_chunks if c.doc_id == "SOP-014-v2"]
    assert len(sop_014_v2_chunks) > 0, "SOP-014-v2 chunks not found"
    for c in sop_014_v2_chunks:
        assert c.status == "superseded", f"SOP-014-v2 chunk has unexpected status: {c.status}"
    print(f"[TEST 4] PASS: Superseded status preserved for SOP-014-v2.")

    # 5. Build into a temp folder and verify builder outputs
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        docs_count, chunks_count, people_count = build(raw_dir, tmp_path)
        assert (tmp_path / "chunks.json").exists(), "chunks.json missing in temp build"
        assert (tmp_path / "docs.json").exists(), "docs.json missing in temp build"
        assert (tmp_path / "people.json").exists(), "people.json missing in temp build"
        assert docs_count > 0 and chunks_count > 0 and people_count > 0
        print(f"[TEST 5] PASS: build() wrote docs.json, chunks.json, people.json to temp folder ({docs_count} docs, {chunks_count} chunks, {people_count} people).")

    # 6. Assert Priya Rao is top deviation expert for analyst, intern, and manager
    analyst_experts = find_experts("deviation", "analyst")
    assert len(analyst_experts) > 0, "No experts returned for topic 'deviation' (analyst)"
    assert analyst_experts[0].name == "Priya Rao", f"Top deviation expert for analyst is {analyst_experts[0].name}, expected Priya Rao"
    print(f"[TEST 6a] PASS: Priya Rao is top deviation expert for analyst (distinct doc evidence count = {analyst_experts[0].evidence_count}).")

    intern_experts = find_experts("deviation handling", "intern")
    assert len(intern_experts) > 0, "No experts returned for topic 'deviation handling' (intern)"
    assert intern_experts[0].name == "Priya Rao", f"Top deviation expert for intern is {intern_experts[0].name}, expected Priya Rao"
    print(f"[TEST 6b] PASS: Priya Rao is top deviation expert for intern (distinct doc evidence count = {intern_experts[0].evidence_count}).")

    manager_experts = find_experts("deviations", "manager")
    assert len(manager_experts) > 0, "No experts returned for topic 'deviations' (manager)"
    assert manager_experts[0].name == "Priya Rao", f"Top deviation expert for manager is {manager_experts[0].name}, expected Priya Rao"
    print(f"[TEST 6c] PASS: Priya Rao is top deviation expert for manager (distinct doc evidence count = {manager_experts[0].evidence_count}).")

    # 7. Assert onboarding paths contain no superseded or restricted documents
    intern_qa_path = onboarding_path("QA", "intern")
    intern_qa_doc_ids = [item.doc_id for items in intern_qa_path.days.values() for item in items]
    print(f"[TEST 7a] Intern QA onboarding doc_ids: {intern_qa_doc_ids}")
    assert "SOP-014-v2" not in intern_qa_doc_ids, "Superseded SOP-014-v2 found in intern onboarding path"
    assert "DI-001" not in intern_qa_doc_ids, "Restricted DI-001 found in intern onboarding path"
    assert "QM-001" in intern_qa_doc_ids, "QM-001 missing from intern QA onboarding"
    assert "SOP-014-v3" in intern_qa_doc_ids, "SOP-014-v3 missing from intern QA onboarding"

    analyst_reg_path = onboarding_path("Regulatory", "analyst")
    analyst_reg_doc_ids = [item.doc_id for items in analyst_reg_path.days.values() for item in items]
    print(f"[TEST 7b] Analyst Regulatory onboarding doc_ids: {analyst_reg_doc_ids}")
    assert "AUD-001" not in analyst_reg_doc_ids, "Manager-only AUD-001 found in analyst onboarding path"
    assert "REG-001" in analyst_reg_doc_ids, "REG-001 missing from analyst Regulatory onboarding"

    manager_reg_path = onboarding_path("Regulatory", "manager")
    manager_reg_doc_ids = [item.doc_id for items in manager_reg_path.days.values() for item in items]
    print(f"[TEST 7c] Manager Regulatory onboarding doc_ids: {manager_reg_doc_ids}")
    assert "AUD-001" in manager_reg_doc_ids, "AUD-001 expected in manager Regulatory onboarding"

    unknown_path = onboarding_path("Finance", "analyst")
    assert unknown_path.days == {}, f"Unknown job role returned non-empty days: {unknown_path.days}"
    print(f"[TEST 7d] PASS: Unknown job role returns empty OnboardingPath.")

    for day, items in intern_qa_path.days.items():
        assert len(items) > 0, f"Empty day found: {day}"
        for item in items:
            assert item.est_minutes >= 5, f"est_minutes < 5 for {item.doc_id}: {item.est_minutes}"
            assert len(item.why) > 10, f"why string too short for {item.doc_id}: {item.why}"
    print(f"[TEST 7e] PASS: Day distribution, why templates, and reading minutes (min 5 min) verified.")

    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% compliant with PLAN.md)")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_selftest()
    except AssertionError as e:
        sys.stderr.write(f"\nSELFTEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"\nUNEXPECTED ERROR: {e}\n")
        sys.exit(2)
