"""Onboarding reading path module for Provenance.

Generates role-tailored 5-day reading curricula for new joiners in QA, Production, and Regulatory roles.
Filters out superseded documents and documents restricted for the user's role.
Estimates reading time at 200 words per minute (minimum 5 minutes).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from contracts import OnboardingPath, ReadingItem, Role
import app.config as config

# Hardcoded ordered doc_id lists from Section 6 and Dev 2 spec
JOB_ROLE_PATHS: dict[str, list[str]] = {
    "QA": ["ONB-001", "QM-001", "SOP-001", "DI-001", "SOP-021", "SOP-014-v3"],
    "Production": ["QM-001", "SOP-014-v3", "EQP-001", "SOP-001", "STB-001"],
    "Regulatory": ["QM-001", "REG-001", "DI-001", "SOP-021", "AUD-001"],
}

# Deterministic rationale template per primary topic
WHY_TEMPLATES: dict[str, str] = {
    "onboarding": "Essential orientation guide and onboarding expectations for your role.",
    "new-joiner": "Foundational guidance and key departmental contacts for new team members.",
    "quality-system": "Core governance manual outlining pharmaceutical quality management standards.",
    "deviation": "Standard operating procedure for logging, categorizing, and managing deviations.",
    "capa": "Requirements for root cause analysis and corrective action closure timelines.",
    "oos": "Investigation protocols and escalation timelines for out-of-specification results.",
    "cold-chain": "Critical temperature control specifications and cold-chain handling rules.",
    "storage-temperature": "Warehouse storage limits and excursion quarantine requirements.",
    "data-integrity": "Regulatory policy governing ALCOA+ data integrity and electronic records.",
    "regulatory": "Overview of health authority guidelines and inspection readiness expectations.",
    "equipment": "Standard operation and qualification instructions for critical facility equipment.",
    "stability": "Protocols and reporting requirements for drug product stability testing.",
    "audit": "Summary of audit observations and compliance remediation commitments.",
}


def load_doc_records() -> dict[str, dict]:
    """Load document records from processed docs.json when present, or derive from get_all_chunks()."""
    docs_file = config.PROCESSED_DIR / "docs.json"
    if docs_file.exists():
        try:
            with open(docs_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                return {item["doc_id"]: item for item in items}
        except Exception as e:
            sys.stderr.write(f"Warning reading {docs_file}: {e}\n")

    # Fallback: derive records from chunks
    from modules.ingestion.experts import get_all_chunks

    chunks = get_all_chunks()
    records: dict[str, dict] = {}
    for c in chunks:
        words = len(c.text.split())
        if c.doc_id not in records:
            records[c.doc_id] = {
                "doc_id": c.doc_id,
                "title": c.title,
                "allowed_roles": c.allowed_roles,
                "status": c.status,
                "topics": c.topics,
                "word_count": words,
            }
        else:
            records[c.doc_id]["word_count"] += words
    return records


def build_why_line(topics: list[str]) -> str:
    """Produce a deterministic one-line rationale from topic templates."""
    for t in topics:
        if t in WHY_TEMPLATES:
            return WHY_TEMPLATES[t]
    return "Essential compliance and quality procedure for your role at Novacure Labs."


def onboarding_path(job_role: str, role: Role) -> OnboardingPath:
    """Generate an onboarding reading path for job_role and role.

    - Unknown job roles return an empty OnboardingPath (empty days).
    - Hardcoded ordered doc_id lists:
        QA: ONB-001, QM-001, SOP-001, DI-001, SOP-021, SOP-014-v3
        Production: QM-001, SOP-014-v3, EQP-001, SOP-001, STB-001
        Regulatory: QM-001, REG-001, DI-001, SOP-021, AUD-001
    - Keep only documents that the role may see AND are current (never superseded).
    - Place first two items on Day 1, then one item per day up to Day 5.
    - Omit empty days.
    - Deterministic why from template per topic.
    - Estimate minutes from word count (200 words/min, minimum 5).
    """
    try:
        # Match job role case-insensitively
        matched_job_role = None
        for canonical in JOB_ROLE_PATHS:
            if canonical.lower() == job_role.strip().lower():
                matched_job_role = canonical
                break

        if not matched_job_role:
            return OnboardingPath(job_role=job_role, days={})

        doc_ids = JOB_ROLE_PATHS[matched_job_role]
        doc_records = load_doc_records()

        valid_items: list[ReadingItem] = []
        order_idx = 1

        for doc_id in doc_ids:
            doc = doc_records.get(doc_id)
            if not doc:
                continue

            # Must be current (never superseded)
            if doc.get("status") != "current":
                continue

            # Role must be allowed
            allowed = doc.get("allowed_roles", [])
            if role not in allowed:
                continue

            word_count = doc.get("word_count", 600)
            est_minutes = max(5, round(word_count / 200))
            topics = doc.get("topics", [])
            why_text = build_why_line(topics)

            valid_items.append(
                ReadingItem(
                    order=order_idx,
                    doc_id=doc_id,
                    title=doc.get("title", doc_id),
                    why=why_text,
                    est_minutes=est_minutes,
                )
            )
            order_idx += 1

        if not valid_items:
            return OnboardingPath(job_role=matched_job_role, days={})

        # Distribute: first 2 on Day 1, then 1 per day up to Day 5
        days: dict[str, list[ReadingItem]] = {}
        if len(valid_items) >= 1:
            days["Day 1"] = valid_items[:2]

        remaining = valid_items[2:]
        day_num = 2
        for item in remaining:
            if day_num > 5:
                # Any extra append to Day 5
                days["Day 5"].append(item)
            else:
                days[f"Day {day_num}"] = [item]
                day_num += 1

        return OnboardingPath(job_role=matched_job_role, days=days)
    except Exception as e:
        sys.stderr.write(f"Error in onboarding_path(job_role={job_role}, role={role}): {e}\n")
        return OnboardingPath(job_role=job_role, days={})
