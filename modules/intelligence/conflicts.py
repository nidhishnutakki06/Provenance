import re
import sys
from typing import Optional
from contracts import Chunk, Citation, Conflict
from app import llm

TEMP_REGEX = re.compile(
    r'(\d+(?:\.\d+)?)\s*(?:to|-|–|—)\s*(\d+(?:\.\d+)?)\s*°\s*[cC]',
    re.IGNORECASE
)


def _extract_sentence(text: str, start: int, end: int) -> str:
    """Extract the sentence enclosing the specified character range."""
    # Look back for preceding sentence boundary
    prev_boundary = 0
    for match in re.finditer(r'(?<=[.!?\n])\s+', text[:start]):
        prev_boundary = match.end()

    # Look forward for following sentence boundary
    next_boundary = len(text)
    next_match = re.search(r'[.!?\n]', text[end:])
    if next_match:
        next_boundary = end + next_match.end()

    sentence = text[prev_boundary:next_boundary].strip()
    return sentence if sentence else text[start:end]


def detect_conflicts(chunks: list[Chunk]) -> list[Conflict]:
    """Detect superseded documents and temperature range contradictions among chunks.

    Returns at most 3 conflicts.
    """
    if not chunks:
        return []

    try:
        # -------------------------------------------------------------
        # (a) Staleness: every chunk whose status is superseded becomes
        # a Conflict of kind superseded. Deduplicate one per superseded document.
        # -------------------------------------------------------------
        seen_superseded_docs: set[str] = set()
        staleness_conflicts: list[Conflict] = []

        for chunk in chunks:
            if chunk.status != 'superseded':
                continue
            if chunk.doc_id in seen_superseded_docs:
                continue
            seen_superseded_docs.add(chunk.doc_id)

            # Find the document in the list whose supersedes equals this doc_id
            newer_chunk = next((c for c in chunks if c.supersedes == chunk.doc_id), None)

            source_a = Citation(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                title=chunk.title,
                source_type=chunk.source_type,
                version=chunk.version,
                date=chunk.date,
                status=chunk.status,
                snippet=chunk.text[:200],
                location=chunk.location,
            )

            if newer_chunk:
                source_b = Citation(
                    chunk_id=newer_chunk.chunk_id,
                    doc_id=newer_chunk.doc_id,
                    title=newer_chunk.title,
                    source_type=newer_chunk.source_type,
                    version=newer_chunk.version,
                    date=newer_chunk.date,
                    status=newer_chunk.status,
                    snippet=newer_chunk.text[:200],
                    location=newer_chunk.location,
                )
                explanation = f"{chunk.title} ({chunk.doc_id}) is superseded by {newer_chunk.title} ({newer_chunk.doc_id})."
                recommendation = f"Use {newer_chunk.title} ({newer_chunk.doc_id}) instead of superseded document {chunk.doc_id}."
            else:
                source_b = Citation(
                    chunk_id=f"{chunk.doc_id}#newer",
                    doc_id=f"{chunk.doc_id}-vCurrent",
                    title=f"Newer version of {chunk.title}",
                    source_type=chunk.source_type,
                    version=None,
                    date=chunk.date,
                    status="current",
                    snippet="A newer version exists replacing this document.",
                    location="document",
                )
                explanation = f"{chunk.title} ({chunk.doc_id}) is superseded. A newer version exists."
                recommendation = f"Consult the latest revision; {chunk.doc_id} has been superseded."

            topic = "cold-chain storage temperature" if any(
                t in ("cold-chain", "storage-temperature") for t in chunk.topics
            ) else (chunk.topics[0] if chunk.topics else "cold-chain storage temperature")

            staleness_conflicts.append(Conflict(
                topic=topic,
                kind="superseded",
                explanation=explanation,
                source_a=source_a,
                source_b=source_b,
                recommendation=recommendation
            ))

        # -------------------------------------------------------------
        # (b) Contradictions: group non-superseded chunks by topic
        # across DIFFERENT doc_ids; extract temperature ranges.
        # -------------------------------------------------------------
        non_superseded = [c for c in chunks if c.status != 'superseded']
        contradiction_conflicts: list[Conflict] = []

        doc_range_entries: list[dict] = []
        for c in non_superseded:
            matches = list(TEMP_REGEX.finditer(c.text))
            for m in matches:
                low = float(m.group(1))
                high = float(m.group(2))
                range_str = f"{m.group(1)} to {m.group(2)} °C"
                snippet = _extract_sentence(c.text, m.start(), m.end())
                doc_range_entries.append({
                    "chunk": c,
                    "doc_id": c.doc_id,
                    "topics": c.topics if c.topics else ["cold-chain storage temperature"],
                    "range_key": (low, high),
                    "range_str": range_str,
                    "snippet": snippet,
                    "date": c.date,
                })

        all_topics: set[str] = set()
        for entry in doc_range_entries:
            for t in entry["topics"]:
                all_topics.add(t)

        llm_called = False
        seen_range_pairs: set[tuple] = set()

        for topic in sorted(all_topics):
            topic_entries = [e for e in doc_range_entries if topic in e["topics"]]
            ranges_in_topic: dict[tuple, list[dict]] = {}
            for e in topic_entries:
                ranges_in_topic.setdefault(e["range_key"], []).append(e)

            distinct_ranges = list(ranges_in_topic.keys())
            if len(distinct_ranges) < 2:
                continue

            for i in range(len(distinct_ranges)):
                for j in range(i + 1, len(distinct_ranges)):
                    r1 = distinct_ranges[i]
                    r2 = distinct_ranges[j]
                    norm_pair = tuple(sorted([r1, r2]))
                    if norm_pair in seen_range_pairs:
                        continue
                    seen_range_pairs.add(norm_pair)

                    entries_1 = ranges_in_topic[r1]
                    entries_2 = ranges_in_topic[r2]

                    chosen_pair = None
                    for e1 in entries_1:
                        for e2 in entries_2:
                            if e1["doc_id"] != e2["doc_id"]:
                                chosen_pair = (e1, e2)
                                break
                        if chosen_pair:
                            break

                    if not chosen_pair:
                        continue

                    e_a, e_b = chosen_pair
                    chunk_a = e_a["chunk"]
                    chunk_b = e_b["chunk"]
                    range_str_a = e_a["range_str"]
                    range_str_b = e_b["range_str"]
                    snippet_a = e_a["snippet"]
                    snippet_b = e_b["snippet"]

                    source_a = Citation(
                        chunk_id=chunk_a.chunk_id,
                        doc_id=chunk_a.doc_id,
                        title=chunk_a.title,
                        source_type=chunk_a.source_type,
                        version=chunk_a.version,
                        date=chunk_a.date,
                        status=chunk_a.status,
                        snippet=snippet_a,
                        location=chunk_a.location,
                    )
                    source_b = Citation(
                        chunk_id=chunk_b.chunk_id,
                        doc_id=chunk_b.doc_id,
                        title=chunk_b.title,
                        source_type=chunk_b.source_type,
                        version=chunk_b.version,
                        date=chunk_b.date,
                        status=chunk_b.status,
                        snippet=snippet_b,
                        location=chunk_b.location,
                    )

                    explanation = ""
                    recommendation = ""

                    # Call LLM once if not yet called
                    if not llm_called:
                        llm_called = True
                        prompt = (
                            f"Compare these conflicting pharmaceutical documents and return a JSON object with keys 'explanation' and 'recommendation'.\n"
                            f"Source A ({chunk_a.title}, {chunk_a.doc_id}, date {chunk_a.date}): \"{snippet_a}\" states {range_str_a}.\n"
                            f"Source B ({chunk_b.title}, {chunk_b.doc_id}, date {chunk_b.date}): \"{snippet_b}\" states {range_str_b}.\n"
                            f"Return JSON only with keys explanation and recommendation."
                        )
                        try:
                            llm_res = llm.complete_json(prompt)
                            if isinstance(llm_res, dict):
                                explanation = llm_res.get("explanation", "").strip()
                                recommendation = llm_res.get("recommendation", "").strip()
                        except Exception as e:
                            print(f"Error calling complete_json: {e}", file=sys.stderr)

                    # Deterministic fallback if LLM result is empty
                    if not explanation or not recommendation:
                        if chunk_b.date >= chunk_a.date:
                            newer_chunk, older_chunk = chunk_b, chunk_a
                            newer_range, older_range = range_str_b, range_str_a
                        else:
                            newer_chunk, older_chunk = chunk_a, chunk_b
                            newer_range, older_range = range_str_a, range_str_b

                        combined = (newer_chunk.text + " " + older_chunk.text + " " + snippet_a + " " + snippet_b).lower()
                        is_pending = "pending revision" in combined or "until sop-014 is revised" in combined or "revised" in combined

                        pending_text = " pending official SOP revision" if is_pending else ""
                        explanation = (
                            f"{older_chunk.title} ({older_chunk.doc_id}) specifies {older_range}, whereas the newer document "
                            f"{newer_chunk.title} ({newer_chunk.doc_id}, dated {newer_chunk.date}) specifies {newer_range}"
                            f"{pending_text}."
                        )
                        recommendation = (
                            f"Follow the newest source ({newer_chunk.title}, {newer_chunk.doc_id}: {newer_range}) while confirming with QA."
                        )

                    conflict_topic = "cold-chain storage temperature" if topic in (
                        "cold-chain", "storage-temperature", "cold-chain storage temperature"
                    ) else topic

                    contradiction_conflicts.append(Conflict(
                        topic=conflict_topic,
                        kind="contradiction",
                        explanation=explanation,
                        source_a=source_a,
                        source_b=source_b,
                        recommendation=recommendation
                    ))

        # Combine conflicts, prioritizing contradictions and staleness, up to 3
        all_conflicts = contradiction_conflicts + staleness_conflicts
        return all_conflicts[:3]

    except Exception as e:
        print(f"Error in detect_conflicts: {e}", file=sys.stderr)
        return []
