"""Expert finder module for Provenance.

Identifies topic experts based on evidence in documents (authors, email senders,
Teams participants, and named mentions from Section 6.1).
Enforces role-based security: evidence is only counted in chunks viewable by the user's role.
"""

from __future__ import annotations

import json
import re
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

# Topic normalization synonyms/keywords ("ich" removed from regulatory)
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
    "regulatory": ["regulatory", "health authority", "guideline"],
    "quality-system": ["quality-system", "quality system", "quality manual", "gmp", "cgmp"],
    "new-joiner": ["new-joiner", "new joiner", "new joiners"],
}


def normalize_topic(query_topic: str) -> str:
    """Normalize a free-text topic string to the Section 5.5 vocabulary.

    - Keeps exact vocabulary match first.
    - Matches a synonym only when it appears in the query as a whole word or phrase,
      using regex (?<![a-z0-9])<escaped synonym>(?![a-z0-9]).
    - No reverse substring testing.
    """
    if not query_topic:
        return ""
    q = query_topic.strip().lower()

    # Exact vocabulary match first
    if q in TOPIC_VOCABULARY:
        return q

    # Match synonym as whole word/phrase only
    for canon_topic, synonyms in TOPIC_SYNONYMS.items():
        for syn in synonyms:
            pattern = rf"(?<![a-z0-9]){re.escape(syn.lower())}(?![a-z0-9])"
            if re.search(pattern, q):
                return canon_topic

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
    - Counts evidence per DISTINCT DOCUMENT, not per chunk.
    - Sorts with key (-len(docs), -chunk_count, name ascending).
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

        person_matching_docs: dict[str, set[str]] = defaultdict(set)
        person_chunk_counts: dict[str, int] = defaultdict(int)
        person_doc_chunk_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        doc_titles: dict[str, str] = {}
        person_role_topics: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        topic_pattern = rf"(?<![a-z0-9]){re.escape(norm_topic.replace('-', ' '))}(?![a-z0-9])"
        topic_pattern_raw = rf"(?<![a-z0-9]){re.escape(norm_topic)}(?![a-z0-9])"

        for chunk in role_chunks:
            doc_titles[chunk.doc_id] = chunk.title
            chunk_matches_topic = (
                norm_topic in chunk.topics
                or bool(re.search(topic_pattern, chunk.text.lower()))
                or bool(re.search(topic_pattern_raw, chunk.text.lower()))
                or bool(re.search(topic_pattern, chunk.title.lower()))
            )

            for person_name in PEOPLE_TITLE_MAP:
                is_author = person_name.lower() in chunk.author.lower()
                is_in_text = person_name.lower() in chunk.text.lower()
                if is_author or is_in_text:
                    for t in chunk.topics:
                        person_role_topics[person_name][t] += 1

                    if chunk_matches_topic:
                        person_matching_docs[person_name].add(chunk.doc_id)
                        person_chunk_counts[person_name] += 1
                        person_doc_chunk_counts[person_name][chunk.doc_id] += 1

        candidates = []
        for person_name in PEOPLE_TITLE_MAP:
            docs_set = person_matching_docs.get(person_name, set())
            if not docs_set:
                continue
            candidates.append(
                {
                    "name": person_name,
                    "docs": docs_set,
                    "chunk_count": person_chunk_counts[person_name],
                }
            )

        if not candidates:
            return []

        # Sort key: (-len(docs), -chunk_count, name ascending)
        candidates.sort(key=lambda x: (-len(x["docs"]), -x["chunk_count"], x["name"]))

        experts: list[Expert] = []
        for cand in candidates[:3]:
            name = cand["name"]
            docs_set = cand["docs"]

            # sample_source = title of the person's document with the most matching chunks
            top_doc_id = max(person_doc_chunk_counts[name].items(), key=lambda item: item[1])[0]
            sample_source = doc_titles.get(top_doc_id, top_doc_id)

            # topics = top 3 topics from the role-visible chunks only
            top_topics_sorted = [
                t
                for t, _ in sorted(
                    person_role_topics[name].items(), key=lambda item: item[1], reverse=True
                )
            ]
            top_topics = top_topics_sorted[:3] if top_topics_sorted else [norm_topic]

            experts.append(
                Expert(
                    name=name,
                    role=PEOPLE_TITLE_MAP.get(name, "Subject Matter Expert"),
                    evidence_count=len(docs_set),
                    topics=top_topics,
                    sample_source=sample_source,
                )
            )

        return experts
    except Exception as e:
        sys.stderr.write(f"Error in find_experts(topic={topic}, role={role}): {e}\n")
        return []
