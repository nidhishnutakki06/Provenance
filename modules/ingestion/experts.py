"""Expert finder module for Provenance.

Identifies topic experts based on evidence in documents (authors, email senders,
Teams participants, and named mentions from Section 6.1).
Enforces role-based security: evidence is only counted in chunks viewable by the user's role.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

from contracts import Chunk, Expert, Role
import app.config as config
from modules.ingestion.connectors import (
    EmailConnector,
    SharePointConnector,
    SopConnector,
    TeamsConnector,
)

# Section 6.1 Name-to-Title hardcoded mapping
PEOPLE_TITLE_MAP: dict[str, str] = {
    "Dr. Meera Iyer": "QA Head",
    "Priya Rao": "QA Lead",
    "Arjun Menon": "Cold-Chain Supervisor",
    "Sana Khan": "QA Analyst",
    "Kavya Nair": "Regulatory Affairs Manager",
    "Vikram Shah": "Production Manager",
    "Rahul Verma": "New QA joiner",
}

# Section 5.5 Topic vocabulary
TOPIC_VOCABULARY = [
    "deviation",
    "capa",
    "oos",
    "cold-chain",
    "storage-temperature",
    "audit",
    "onboarding",
    "data-integrity",
    "stability",
    "equipment",
    "regulatory",
    "quality-system",
    "new-joiner",
]

# Topic normalization synonyms/keywords
TOPIC_SYNONYMS: dict[str, list[str]] = {
    "deviation": ["deviation", "deviations", "deviation handling", "variance", "incident"],
    "capa": ["capa", "corrective action", "preventive action", "corrective and preventive"],
    "oos": ["oos", "out of specification", "out-of-specification"],
    "cold-chain": ["cold-chain", "cold chain", "cold storage", "vaccine storage"],
    "storage-temperature": ["storage-temperature", "storage temperature", "temperature", "excursion"],
    "audit": ["audit", "inspection", "audit findings"],
    "onboarding": ["onboarding", "new hire", "welcome guide", "orientation", "training"],
    "data-integrity": ["data-integrity", "data integrity", "alcoa", "21 cfr"],
    "stability": ["stability", "shelf life", "shelf-life", "degradation"],
    "equipment": ["equipment", "freezer", "refrigerator", "unit manual"],
    "regulatory": ["regulatory", "ich", "health authority", "guideline"],
    "quality-system": ["quality-system", "quality system", "quality manual", "gmp", "cgmp"],
    "new-joiner": ["new-joiner", "new joiner", "new joiners"],
}


def normalize_topic(query_topic: str) -> str:
    """Normalize a free-text topic string to the Section 5.5 vocabulary."""
    if not query_topic:
        return ""
    q = query_topic.strip().lower()

    # Exact vocabulary match
    if q in TOPIC_VOCABULARY:
        return q

    # Check synonyms
    for canon_topic, synonyms in TOPIC_SYNONYMS.items():
        for syn in synonyms:
            if syn in q or q in syn:
                return canon_topic

    # Substring check against vocabulary
    for vocab in TOPIC_VOCABULARY:
        if vocab.replace("-", " ") in q or vocab in q:
            return vocab

    return ""


def get_all_chunks(raw_dir: Optional[Path] = None) -> list[Chunk]:
    """Retrieve chunks from processed file or directly from connectors."""
    chunks_file = config.PROCESSED_DIR / "chunks.json"
    if chunks_file.exists():
        try:
            with open(chunks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Chunk(**item) for item in data]
        except Exception as e:
            sys.stderr.write(f"Warning reading {chunks_file}: {e}\n")

    # Fallback to loading via connectors
    target_raw = raw_dir or config.raw_dir()
    chunks: list[Chunk] = []
    chunks.extend(SharePointConnector().load(target_raw))
    chunks.extend(SopConnector().load(target_raw))
    chunks.extend(EmailConnector().load(target_raw))
    chunks.extend(TeamsConnector().load(target_raw))
    return chunks


def find_experts(topic: str, role: Role) -> list[Expert]:
    """Find up to 3 domain experts for a topic filtered by the requesting role.

    - Normalizes the topic to Section 5.5 vocabulary.
    - Counts evidence ONLY in chunks the given role may see.
    - Priya Rao ranks first for every role on 'deviation'.
    - Never raises on bad input.
    """
    try:
        norm_topic = normalize_topic(topic)
        if not norm_topic:
            return []

        chunks = get_all_chunks()
        # Filter strictly by user role first (security rule 8)
        role_chunks = [c for c in chunks if role in c.allowed_roles]

        # Track evidence per person:
        # person -> {count: int, doc_counts: dict[title, count], topic_counts: dict[topic, count]}
        person_evidence: dict[str, dict] = defaultdict(
            lambda: {"count": 0, "doc_counts": defaultdict(int), "topic_counts": defaultdict(int)}
        )

        for chunk in role_chunks:
            # Check if chunk relates to the target topic
            chunk_matches_topic = (
                norm_topic in chunk.topics
                or norm_topic.replace("-", " ") in chunk.text.lower()
                or norm_topic.replace("-", " ") in chunk.title.lower()
            )
            if not chunk_matches_topic:
                continue

            # Check mentions for known people
            for person_name in PEOPLE_TITLE_MAP:
                is_author = person_name.lower() in chunk.author.lower()
                is_in_text = person_name.lower() in chunk.text.lower()
                if is_author or is_in_text:
                    person_evidence[person_name]["count"] += 1
                    person_evidence[person_name]["doc_counts"][chunk.title] += 1
                    for t in chunk.topics:
                        person_evidence[person_name]["topic_counts"][t] += 1

        # Also collect other topics for each person across all their viewable chunks
        for chunk in role_chunks:
            for person_name in PEOPLE_TITLE_MAP:
                if person_name in person_evidence:
                    if (
                        person_name.lower() in chunk.author.lower()
                        or person_name.lower() in chunk.text.lower()
                    ):
                        for t in chunk.topics:
                            person_evidence[person_name]["topic_counts"][t] += 1

        if not person_evidence:
            return []

        # Sort descending by evidence count
        sorted_people = sorted(
            person_evidence.items(),
            key=lambda item: (item[1]["count"], item[0]),
            reverse=True,
        )

        experts: list[Expert] = []
        for name, data in sorted_people:
            if data["count"] <= 0:
                continue

            # Most frequent document source
            sample_src = ""
            if data["doc_counts"]:
                sample_src = max(data["doc_counts"].items(), key=lambda x: x[1])[0]

            # Top 3 topics
            sorted_topics = [
                t for t, _ in sorted(data["topic_counts"].items(), key=lambda x: x[1], reverse=True)
            ]
            top_topics = sorted_topics[:3] if sorted_topics else [norm_topic]

            experts.append(
                Expert(
                    name=name,
                    role=PEOPLE_TITLE_MAP.get(name, "Subject Matter Expert"),
                    evidence_count=data["count"],
                    topics=top_topics,
                    sample_source=sample_src,
                )
            )
            if len(experts) >= 3:
                break

        return experts
    except Exception as e:
        sys.stderr.write(f"Error in find_experts(topic={topic}, role={role}): {e}\n")
        return []
