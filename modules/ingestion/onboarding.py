"""Onboarding reading path module for Provenance.

Generates role-tailored 5-day reading curricula for new joiners in QA, Production, and Regulatory roles.
Filters out superseded documents and documents restricted for the user's role.
Estimates reading time at 200 words per minute (minimum 5 minutes).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from contracts import OnboardingPath, ReadingItem, Role
import app.config as config
from modules.ingestion.connectors import load_sidecar

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

# Section 6.2 fallback catalogue in case corpus is partially indexed
DOC_CATALOGUE: dict[str, dict] = {
    "ONB-001": {
        "title": "New QA Hire Onboarding Guide",
        "allowed_roles": ["intern", "analyst", "manager"],
        "status": "current",
        "topics": ["onboarding", "new-joiner", "deviation"],
        "word_count": 550,
    },
    "QM-001": {
        "title": "Quality Manual",
        "allowed_roles": ["intern", "analyst", "manager"],
        "status": "current",
        "topics": ["quality-system", "deviation"],
        "word_count": 1200,
    },
    "SOP-001": {
        "title": "SOP-001 Deviation Handling",
        "allowed_roles": ["intern", "analyst", "manager"],
        "status": "current",
        "topics": ["deviation", "quality-system"],
        "word_count": 800,
    },
    "DI-001": {
        "title": "Data Integrity Policy",
        "allowed_roles": ["analyst", "manager"],
        "status": "current",
        "topics": ["data-integrity", "quality-system"],
        "word_count": 950,
    },
    "SOP-021": {
        "title": "SOP-021 CAPA Management",
        "allowed_roles": ["analyst", "manager"],
        "status": "current",
        "topics": ["capa", "oos", "deviation"],
        "word_count": 1100,
    },
    "SOP-014-v3": {
        "title": "SOP-014 Cold-Chain Storage v3",
        "allowed_roles": ["intern", "analyst", "manager"],
        "status": "current",
        "topics": ["cold-chain", "storage-temperature"],
        "word_count": 850,
    },
    "EQP-001": {
        "title": "Cold Storage Unit Equipment Manual",
        "allowed_roles": ["analyst", "manager"],
        "status": "current",
        "topics": ["equipment", "cold-chain"],
        "word_count": 1400,
    },
    "STB-001": {
        "title": "Stability Study Report",
        "allowed_roles": ["analyst", "manager"],
        "status": "current",
        "topics": ["stability", "storage-temperature"],
        "word_count": 1050,
    },
    "REG-001": {
        "title": "Regulatory Guideline Summary",
        "allowed_roles": ["analyst", "manager"],
        "status": "current",
        "topics": ["regulatory", "data-integrity"],
        "word_count": 900,
    },
    "AUD-001": {
        "title": "Audit Findings Summary",
        "allowed_roles": ["manager"],
        "status": "current",
        "topics": ["audit", "deviation", "cold-chain"],
        "word_count": 750,
    },
    "SOP-014-v2": {
        "title": "SOP-014 Cold-Chain Storage v2",
        "allowed_roles": ["analyst", "manager"],
        "status": "superseded",
        "topics": ["cold-chain", "storage-temperature"],
        "word_count": 800,
    },
}


def load_doc_records() -> dict[str, dict]:
    """Load document records from processed docs.json, falling back to sidecars and catalogue."""
    records: dict[str, dict] = {}

    docs_file = config.PROCESSED_DIR / "docs.json"
    if docs_file.exists():
        try:
            with open(docs_file, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    records[item["doc_id"]] = item
            return records
        except Exception as e:
            sys.stderr.write(f"Warning reading {docs_file}: {e}\n")

    # Inspect sidecars in raw_dir()
    raw_dir = config.raw_dir()
    if raw_dir.is_dir():
        for meta_file in raw_dir.rglob("*.meta.json"):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    doc_id = meta.get("doc_id")
                    if doc_id:
                        records[doc_id] = {
                            "doc_id": doc_id,
                            "title": meta.get("title", doc_id),
                            "allowed_roles": meta.get("allowed_roles", []),
                            "status": meta.get("status", "current"),
                            "topics": meta.get("topics", []),
                            "word_count": DOC_CATALOGUE.get(doc_id, {}).get("word_count", 800),
                        }
            except Exception as e:
                sys.stderr.write(f"Error reading sidecar {meta_file}: {e}\n")

    # Merge catalogue fallbacks
    for doc_id, data in DOC_CATALOGUE.items():
        if doc_id not in records:
            records[doc_id] = {"doc_id": doc_id, **data}

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
                days[f"Day 5"].append(item)
            else:
                days[f"Day {day_num}"] = [item]
                day_num += 1

        return OnboardingPath(job_role=matched_job_role, days=days)
    except Exception as e:
        sys.stderr.write(f"Error in onboarding_path(job_role={job_role}, role={role}): {e}\n")
        return OnboardingPath(job_role=job_role, days={})
