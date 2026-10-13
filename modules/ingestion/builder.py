"""Corpus builder module for Provenance.

Runs all connectors on raw_dir, processes documents and chunks, extracts people records,
and writes chunks.json, docs.json, and people.json into out_dir.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from contracts import Chunk
import app.config as config
from modules.ingestion.connectors import (
    EmailConnector,
    SharePointConnector,
    SopConnector,
    TeamsConnector,
    load_sidecar,
)
from modules.ingestion.experts import PEOPLE_TITLE_MAP


def build(raw_dir: Path, out_dir: Path) -> tuple[int, int, int]:
    """Build processed corpus files from raw_dir and save to out_dir.

    Writes:
    - out_dir / chunks.json
    - out_dir / docs.json
    - out_dir / people.json

    Returns (docs_count, chunks_count, people_count).
    Is idempotent and creates out_dir if necessary.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run all four connectors
    sharepoint_conn = SharePointConnector()
    sop_conn = SopConnector()
    email_conn = EmailConnector()
    teams_conn = TeamsConnector()

    all_chunks: list[Chunk] = []
    all_chunks.extend(sharepoint_conn.load(raw_dir))
    all_chunks.extend(sop_conn.load(raw_dir))
    all_chunks.extend(email_conn.load(raw_dir))
    all_chunks.extend(teams_conn.load(raw_dir))

    # 2. Build docs.json records
    # Group chunks by doc_id to compute total word counts
    doc_chunks: dict[str, list[Chunk]] = defaultdict(list)
    for c in all_chunks:
        doc_chunks[c.doc_id].append(c)

    # Find corresponding file path for each doc_id
    doc_file_map: dict[str, str] = {}
    if raw_dir.is_dir():
        for f in raw_dir.rglob("*"):
            if f.is_file() and not f.name.endswith(".meta.json") and not f.name.startswith("."):
                sidecar = load_sidecar(f)
                if sidecar and "doc_id" in sidecar:
                    try:
                        rel_path = str(f.relative_to(raw_dir))
                    except ValueError:
                        rel_path = f.name
                    doc_file_map[sidecar["doc_id"]] = rel_path

    docs_records: list[dict] = []
    seen_docs: set[str] = set()

    for chunk in all_chunks:
        if chunk.doc_id in seen_docs:
            continue
        seen_docs.add(chunk.doc_id)

        doc_c_list = doc_chunks[chunk.doc_id]
        total_words = sum(len(c.text.split()) for c in doc_c_list)
        rel_file = doc_file_map.get(chunk.doc_id, f"{chunk.doc_id}.dat")

        docs_records.append(
            {
                "doc_id": chunk.doc_id,
                "title": chunk.title,
                "source_type": chunk.source_type,
                "version": chunk.version,
                "date": chunk.date,
                "author": chunk.author,
                "owner": chunk.owner,
                "status": chunk.status,
                "supersedes": chunk.supersedes,
                "allowed_roles": chunk.allowed_roles,
                "topics": chunk.topics,
                "word_count": total_words,
                "file": rel_file,
            }
        )

    # 3. Build people.json records
    # Person -> {role, topics: dict[topic, count], sources: set[doc_id], count: int}
    people_data: dict[str, dict] = defaultdict(
        lambda: {"topics": defaultdict(int), "sources": set(), "count": 0}
    )

    for chunk in all_chunks:
        for person_name, person_role in PEOPLE_TITLE_MAP.items():
            is_author = person_name.lower() in chunk.author.lower()
            is_in_text = person_name.lower() in chunk.text.lower()
            if is_author or is_in_text:
                people_data[person_name]["count"] += 1
                people_data[person_name]["sources"].add(chunk.doc_id)
                for t in chunk.topics:
                    people_data[person_name]["topics"][t] += 1

    people_records: list[dict] = []
    for person_name in PEOPLE_TITLE_MAP:
        data = people_data.get(person_name)
        if data and data["count"] > 0:
            people_records.append(
                {
                    "name": person_name,
                    "role": PEOPLE_TITLE_MAP.get(person_name, "Subject Matter Expert"),
                    "topics": dict(data["topics"]),
                    "sources": sorted(list(data["sources"])),
                    "evidence_count": data["count"],
                }
            )

    # Sort people by evidence count descending
    people_records.sort(key=lambda p: p["evidence_count"], reverse=True)

    # 4. Write to out_dir
    chunks_path = out_dir / "chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump([c.model_dump() for c in all_chunks], f, indent=2)

    docs_path = out_dir / "docs.json"
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(docs_records, f, indent=2)

    people_path = out_dir / "people.json"
    with open(people_path, "w", encoding="utf-8") as f:
        json.dump(people_records, f, indent=2)

    print(
        f"Corpus built successfully: {len(docs_records)} docs, "
        f"{len(all_chunks)} chunks, {len(people_records)} people -> {out_dir}"
    )

    return len(docs_records), len(all_chunks), len(people_records)


def build_corpus() -> None:
    """Run all connectors on app.config.raw_dir() and write to app.config.PROCESSED_DIR."""
    try:
        raw_p = config.raw_dir()
        out_p = config.PROCESSED_DIR
        build(raw_p, out_p)
    except Exception as e:
        sys.stderr.write(f"Error in build_corpus(): {e}\n")
    return None
