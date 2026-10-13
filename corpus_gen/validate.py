"""
corpus_gen/validate.py
Validator / selftest for the Novacure Labs corpus.
Performs comprehensive checks against PLAN.md specifications:
  1. Exactly 20 documents and sidecars exist.
  2. Sidecars have required fields and valid vocabulary values.
  3. PDFs yield real text via pypdf.
  4. Access rule in section 6.2 holds.
  5. Every fixed sentence in section 6.3 is present verbatim.
  6. All 7 planted scenarios in section 6.4 hold (including HPLC check and Priya Rao in deviation docs).
Outputs PASS / FAIL per check and exits non-zero on any failure.
"""

import email
import email.policy
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Do NOT import from app/ or modules/
from corpus_gen.manifest import MANIFEST, ALLOWED_TOPICS

DATA_RAW_DIR = Path("data/raw")

EXPECTED_DOC_IDS = {s["doc_id"] for s in MANIFEST}


def extract_document_text(filepath: Path, source_type: str) -> str:
    """Extract full plaintext from any corpus file format."""
    if not filepath.exists():
        return ""

    if source_type in ["sop", "pdf"]:
        import pypdf
        reader = pypdf.PdfReader(str(filepath))
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n".join(text_parts)

    elif source_type == "sharepoint":
        import docx
        doc = docx.Document(str(filepath))
        return "\n".join(p.text for p in doc.paragraphs if p.text)

    elif source_type == "email":
        with open(filepath, "rb") as f:
            msg = email.message_from_binary_file(f, policy=email.policy.default)
            payload = msg.get_content()
            return str(payload)

    elif source_type == "teams":
        with open(filepath, "r", encoding="utf-8") as f:
            messages = json.load(f)
            return "\n".join(m.get("text", "") for m in messages)

    return ""


def run_validations() -> bool:
    all_passed = True

    def record_result(check_name: str, passed: bool, detail: str = "") -> None:
        nonlocal all_passed
        if passed:
            print(f"PASS: {check_name}" + (f" ({detail})" if detail else ""))
        else:
            all_passed = False
            print(f"FAIL: {check_name}" + (f" - {detail}" if detail else ""))

    # -------------------------------------------------------------------------
    # Check 1: Exactly 20 documents and sidecars exist
    # -------------------------------------------------------------------------
    found_doc_ids: Set[str] = set()
    found_files: Dict[str, Tuple[Path, Path, Dict[str, Any]]] = {}

    for spec in MANIFEST:
        doc_id = spec["doc_id"]
        folder = spec["folder"]
        filename = spec["filename"]
        target_file = DATA_RAW_DIR / folder / filename
        sidecar_file = Path(f"{target_file}.meta.json")

        if not target_file.exists():
            record_result(f"File exists: {doc_id}", False, f"Missing {target_file}")
            continue
        if not sidecar_file.exists():
            record_result(f"Sidecar exists: {doc_id}", False, f"Missing {sidecar_file}")
            continue

        try:
            with open(sidecar_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            found_doc_ids.add(doc_id)
            found_files[doc_id] = (target_file, sidecar_file, meta)
        except Exception as e:
            record_result(f"Sidecar parse: {doc_id}", False, str(e))

    doc_count_ok = (len(found_doc_ids) == 20) and (found_doc_ids == EXPECTED_DOC_IDS)
    record_result(
        "Corpus count: exactly 20 doc_ids exist",
        doc_count_ok,
        f"Found {len(found_doc_ids)} matching expected 20"
    )

    if not doc_count_ok:
        return False

    # -------------------------------------------------------------------------
    # Check 2: Sidecar fields and allowed values
    # -------------------------------------------------------------------------
    sidecar_schema_ok = True
    required_keys = {
        "doc_id", "title", "source_type", "version", "date",
        "author", "owner", "status", "supersedes", "allowed_roles", "topics"
    }

    for doc_id, (_, sidecar_path, meta) in found_files.items():
        missing_keys = required_keys - set(meta.keys())
        if missing_keys:
            sidecar_schema_ok = False
            record_result(f"Sidecar schema: {doc_id}", False, f"Missing keys: {missing_keys}")
            break

        if meta["source_type"] not in ["sop", "sharepoint", "email", "teams", "pdf"]:
            sidecar_schema_ok = False
            record_result(f"Sidecar source_type: {doc_id}", False, f"Invalid source_type: {meta['source_type']}")
            break

        if meta["status"] not in ["current", "superseded", "draft"]:
            sidecar_schema_ok = False
            record_result(f"Sidecar status: {doc_id}", False, f"Invalid status: {meta['status']}")
            break

        for r in meta["allowed_roles"]:
            if r not in ["intern", "analyst", "manager"]:
                sidecar_schema_ok = False
                record_result(f"Sidecar roles: {doc_id}", False, f"Invalid role: {r}")
                break

        for t in meta["topics"]:
            if t not in ALLOWED_TOPICS:
                sidecar_schema_ok = False
                record_result(f"Sidecar topics: {doc_id}", False, f"Invalid topic '{t}' not in vocabulary")
                break

    record_result("Sidecar schema and vocabularies valid for all 20 documents", sidecar_schema_ok)

    # -------------------------------------------------------------------------
    # Check 3: Extract text from all documents and verify PDFs with pypdf
    # -------------------------------------------------------------------------
    extracted_texts: Dict[str, str] = {}
    pdf_text_ok = True

    for doc_id, (doc_file, _, meta) in found_files.items():
        st = meta["source_type"]
        text = extract_document_text(doc_file, st)
        extracted_texts[doc_id] = text

        if st in ["sop", "pdf"]:
            if len(text.strip()) < 50:
                pdf_text_ok = False
                record_result(f"PDF extraction: {doc_id}", False, f"Extracted only {len(text.strip())} chars")

    record_result("PDFs yield extractable text via pypdf", pdf_text_ok)

    # -------------------------------------------------------------------------
    # Check 4: Access rule in Section 6.2
    # -------------------------------------------------------------------------
    # Intern sees exactly: Quality Manual (QM-001), onboarding guide (ONB-001),
    # SOP-001, SOP-014-v3, #qa-help (TEAMS-QAHELP), #new-joiners (TEAMS-NEWJOINERS),
    # and the welcome email (EML-005).
    expected_intern = {"QM-001", "ONB-001", "SOP-001", "SOP-014-v3", "TEAMS-QAHELP", "TEAMS-NEWJOINERS", "EML-005"}
    actual_intern = {d for d, (_, _, m) in found_files.items() if "intern" in m["allowed_roles"]}
    intern_access_ok = (actual_intern == expected_intern)
    record_result(
        "Access rule: Intern sees exactly the 7 authorized documents",
        intern_access_ok,
        f"Actual: {actual_intern}"
    )

    # Analyst sees everything except AUD-001 and EML-004.
    expected_analyst = set(EXPECTED_DOC_IDS) - {"AUD-001", "EML-004"}
    actual_analyst = {d for d, (_, _, m) in found_files.items() if "analyst" in m["allowed_roles"]}
    analyst_access_ok = (actual_analyst == expected_analyst)
    record_result(
        "Access rule: Analyst sees 18 documents (everything except AUD-001 and EML-004)",
        analyst_access_ok
    )

    # Manager sees everything.
    actual_manager = {d for d, (_, _, m) in found_files.items() if "manager" in m["allowed_roles"]}
    manager_access_ok = (actual_manager == EXPECTED_DOC_IDS)
    record_result("Access rule: Manager sees all 20 documents", manager_access_ok)

    # -------------------------------------------------------------------------
    # Check 5: Fixed sentences in Section 6.3 present verbatim
    # -------------------------------------------------------------------------
    fixed_checks = [
        ("SOP-014-v3", "Vaccine batches must be stored at 2 to 8 °C."),
        ("SOP-014-v3", "Any temperature excursion longer than 4 hours requires a deviation report."),
        ("SOP-014-v2", "Vaccine batches must be stored at 2 to 8 °C."),
        ("SOP-014-v2", "Temperature excursions of up to 12 hours do not require a deviation report."),
        ("EML-001", "Until SOP-014 is revised, store vaccine batches at 2 to 6 °C."),
        ("TEAMS-COLDCHAIN", "Per Dr. Meera Iyer, hold vaccine batches at 2 to 6 °C until SOP-014 is revised."),
        ("SOP-001", "Every deviation must be reported to QA within 24 hours of discovery."),
        ("SOP-021", "A CAPA must be raised and the investigation completed within 15 working days of an OOS result being confirmed."),
        ("AUD-001", "The audit identified a recurring deviation: temperature excursions in cold-chain storage during Q2 and Q3."),
        ("ONB-001", "In your first week, read the Quality Manual, SOP-001, SOP-021 and the Data Integrity Policy."),
    ]

    fixed_sentences_ok = True
    for doc_id, sentence in fixed_checks:
        doc_text = extracted_texts.get(doc_id, "")
        norm_doc = " ".join(doc_text.split())
        norm_sentence = " ".join(sentence.split())
        if norm_sentence not in norm_doc:
            fixed_sentences_ok = False
            record_result(f"Fixed sentence in {doc_id}", False, f"Missing: '{sentence}'")

    record_result("All section 6.3 fixed sentences appear verbatim", fixed_sentences_ok)

    # -------------------------------------------------------------------------
    # Check 6: Planted Scenarios in Section 6.4 (all 7 scenarios)
    # -------------------------------------------------------------------------
    # Scenario 1 (Conflict): SOP-014-v3 says 2 to 8 °C. EML-001 and TEAMS-COLDCHAIN say 2 to 6 °C.
    s1_ok = (
        ("2 to 8 °C" in extracted_texts.get("SOP-014-v3", "")) and
        ("2 to 6 °C" in extracted_texts.get("EML-001", "")) and
        ("2 to 6 °C" in extracted_texts.get("TEAMS-COLDCHAIN", ""))
    )
    record_result("Planted Scenario 1 (Conflict: 2 to 8 °C vs 2 to 6 °C pending revision)", s1_ok)

    # Scenario 2 (Superseded): SOP-014-v2 has status superseded, supersedes link from v3, and 12h vs 4h rule.
    s2_ok = (
        found_files["SOP-014-v2"][2]["status"] == "superseded" and
        found_files["SOP-014-v3"][2]["supersedes"] == "SOP-014-v2" and
        "12 hours" in extracted_texts.get("SOP-014-v2", "") and
        "4 hours" in extracted_texts.get("SOP-014-v3", "")
    )
    record_result("Planted Scenario 2 (Superseded: SOP-014-v2 superseded with 12h vs 4h rule)", s2_ok)

    # Scenario 3 (Restricted): AUD-001 (manager only) mentions recurring deviation
    s3_ok = (
        found_files["AUD-001"][2]["allowed_roles"] == ["manager"] and
        "recurring deviation" in extracted_texts.get("AUD-001", "").lower()
    )
    record_result("Planted Scenario 3 (Restricted: AUD-001 manager only with audit finding)", s3_ok)

    # Scenario 4 (Unanswerable): No document anywhere contains HPLC or column calibration
    hplc_found = []
    col_cal_found = []
    for doc_id, text in extracted_texts.items():
        if "HPLC" in text:
            hplc_found.append(doc_id)
        if "column calibration" in text.lower():
            col_cal_found.append(doc_id)

    s4_ok = (len(hplc_found) == 0 and len(col_cal_found) == 0)
    record_result(
        "Planted Scenario 4 (Unanswerable: no document contains HPLC or column calibration)",
        s4_ok,
        f"HPLC in {hplc_found}, column calibration in {col_cal_found}" if not s4_ok else "clean"
    )

    # Scenario 5 (Expert): Priya Rao appears in at least 8 documents tagged deviation
    priya_deviation_docs = []
    for doc_id, (_, _, meta) in found_files.items():
        if "deviation" in meta["topics"]:
            text = extracted_texts.get(doc_id, "")
            if "Priya Rao" in text:
                priya_deviation_docs.append(doc_id)

    s5_ok = (len(priya_deviation_docs) >= 8)
    record_result(
        "Planted Scenario 5 (Expert: Priya Rao appears in at least 8 documents tagged deviation)",
        s5_ok,
        f"Appears in {len(priya_deviation_docs)} documents: {priya_deviation_docs}"
    )

    # Scenario 6 (Glossary): SOP-021 defines OOS timeline using CAPA and OOS abbreviations
    sop021_text = extracted_texts.get("SOP-021", "")
    s6_ok = (
        "CAPA" in sop021_text and
        "OOS" in sop021_text and
        "15 working days" in sop021_text
    )
    record_result("Planted Scenario 6 (Glossary: SOP-021 uses CAPA & OOS with 15 working days timeline)", s6_ok)

    # Scenario 7 (Onboarding): QA reading material exists (Quality Manual, SOP-001, SOP-021, Data Integrity Policy, onboarding guide)
    onboarding_docs = {"QM-001", "SOP-001", "SOP-021", "DI-001", "ONB-001"}
    s7_ok = onboarding_docs.issubset(found_doc_ids) and "first week" in extracted_texts.get("ONB-001", "").lower()
    record_result("Planted Scenario 7 (Onboarding: QA reading material documents all present)", s7_ok)

    # Hard rule: REG-001, EQP-001, STB-001 must not state temperature ranges other than 2 to 8 °C
    import re
    range_regex = re.compile(r"(\d+)\s+to\s+(\d+)\s*°?C")
    invalid_ranges = []
    for doc_id in ["REG-001", "EQP-001", "STB-001"]:
        text = extracted_texts.get(doc_id, "")
        for m in range_regex.finditer(text):
            r_str = f"{m.group(1)} to {m.group(2)}"
            if r_str != "2 to 8":
                invalid_ranges.append(f"{doc_id}: {m.group(0)}")

    temp_rule_ok = (len(invalid_ranges) == 0)
    record_result("Hard rule: REG-001, EQP-001, STB-001 state no range other than 2 to 8 °C", temp_rule_ok)

    return all_passed


def main():
    print("=" * 65)
    print("RUNNING CORPUS VALIDATION (Novacure Labs 20-Document Corpus)")
    print("=" * 65)

    passed = run_validations()

    print("=" * 65)
    if passed:
        print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY (PASS)")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED (FAIL)")
        sys.exit(1)


if __name__ == "__main__":
    main()
