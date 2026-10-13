import json
import re
import sys
from typing import Optional

from app import llm
from contracts import AskResponse, Chunk, Citation, Role
from modules.retrieval.index import expand_query, find_expanded_terms, tokenize
from modules.retrieval.search import search_with_scores

# Tuned on the 12 golden questions
MIN_SCORE = 1.5
MIN_TOKEN_SHARE = 0.5


def extract_snippet(text: str, query_tokens: list[str], max_words: int = 40) -> str:
    """Extract the most relevant 40-word window from text based on query tokens."""
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text.strip()

    normalized_words = [re.sub(r'[^a-zA-Z0-9]', '', w).lower() for w in words]
    q_set = {t.lower() for t in query_tokens if t}

    best_score = -1
    best_start = 0

    for i in range(len(words) - max_words + 1):
        window = normalized_words[i : i + max_words]
        score = sum(1 for w in window if w in q_set)
        if score > best_score:
            best_score = score
            best_start = i

    selected = words[best_start : best_start + max_words]
    return " ".join(selected).strip()


def _build_missing_info(question: str) -> str:
    """Create a helpful missing_info message without revealing restricted documents."""
    tokens = tokenize(question, remove_stopwords=True)
    topic_summary = " ".join(tokens) if tokens else "this topic"
    return (
        f"No approved procedures, policies, or records regarding {topic_summary} "
        f"were found in accessible enterprise documents. An official SOP or technical "
        f"specification covering this subject would be required."
    )


def _chunk_to_citation(chunk: Chunk, query_tokens: list[str]) -> Citation:
    return Citation(
        chunk_id=chunk.chunk_id,
        doc_id=chunk.doc_id,
        title=chunk.title,
        source_type=chunk.source_type,
        version=chunk.version,
        date=chunk.date,
        status=chunk.status,
        snippet=extract_snippet(chunk.text, query_tokens, max_words=40),
        location=chunk.location,
    )


def answer(question: str, role: Role) -> AskResponse:
    """
    Answer the user's question for a specific role.
    Core answer only: does not compute conflicts, experts, minutes_saved, or latency_ms.
    """
    try:
        if not question or not question.strip():
            return AskResponse(
                answer="Please provide a question.",
                answerable=False,
                confidence="low",
                citations=[],
                missing_info="No question provided.",
                expanded_terms={},
            )

        expanded_terms = find_expanded_terms(question)
        bm25_tokens, distinctive_tokens = expand_query(question)

        # 1. Take the top 8 chunks
        scored_hits = search_with_scores(question, role, k=8)
        top_chunks = [c for score, c in scored_hits]

        if not scored_hits or not top_chunks:
            return AskResponse(
                answer="I do not have sufficient information in the accessible documents to answer this question.",
                answerable=False,
                confidence="low",
                citations=[],
                missing_info=_build_missing_info(question),
                expanded_terms=expanded_terms,
            )

        top_score = scored_hits[0][0]

        # 2. Answerability Gate:
        # Score only the user's own words minus generic verbs to prevent
        # generic glossary expansion tokens from inflating the token share.
        chunk_tokens: set[str] = set()
        for chunk in top_chunks:
            chunk_tokens.update(
                tokenize(f"{chunk.title} {chunk.text} {' '.join(chunk.topics)}")
            )

        generic_verbs = {'find', 'found', 'show', 'tell', 'give', 'explain', 'need', 'know', 'get'}
        own = set(t for t in tokenize(question, remove_stopwords=True) if t not in generic_verbs)
        if not own:
            own = set(distinctive_tokens)

        overlap = len(own.intersection(chunk_tokens))
        token_share = (overlap / len(own)) if own else 0.0

        if token_share < MIN_TOKEN_SHARE or top_score < MIN_SCORE:
            return AskResponse(
                answer="I do not have sufficient information in the accessible documents to answer this question.",
                answerable=False,
                confidence="low",
                citations=[],
                missing_info=_build_missing_info(question),
                expanded_terms=expanded_terms,
            )

        # 3. Call complete_json with strict system prompt
        system_prompt = (
            "You are a trust-first knowledge assistant for pharma company Novacure Labs.\n"
            "Answer the question ONLY from the numbered passages provided.\n"
            "If passages give different values or conflict, mention each conflicting value with its source document name and prefer current documents over superseded ones.\n"
            "Write citation markers as [n] using the passage numbers for statements supported by that passage.\n"
            "You must respond in valid JSON with these exact keys:\n"
            "- \"answer\": string containing the cited answer text with [n] citation markers.\n"
            "- \"answerable\": boolean (true if answered from passages, false otherwise).\n"
            "- \"confidence\": string (\"high\", \"medium\", or \"low\").\n"
            "- \"used_passages\": list of integers representing the passage numbers cited.\n"
            "- \"missing_info\": string or null (explanation of what source is missing if not answerable).\n"
            "Do not invent any facts not directly stated in the passages."
        )

        passages_text_blocks = []
        for idx, chunk in enumerate(top_chunks, start=1):
            ver_str = f", Version: {chunk.version}" if chunk.version else ""
            passages_text_blocks.append(
                f"[{idx}] Document: {chunk.title} (Doc ID: {chunk.doc_id}{ver_str}, "
                f"Status: {chunk.status}, Date: {chunk.date}, Location: {chunk.location})\n"
                f"{chunk.text}"
            )
        passages_prompt = "\n\n".join(passages_text_blocks)

        user_prompt = (
            f"Question: {question}\n\n"
            f"Passages:\n{passages_prompt}\n\n"
            f"Please return your response in JSON format."
        )

        llm_response = llm.complete_json(user_prompt, system=system_prompt)

        # 4. Fallback if complete_json returns empty dict (mock mode or LLM unavailable)
        if not llm_response or not isinstance(llm_response, dict) or not llm_response.get('answer'):
            hits = top_chunks[:2]
            citations = [_chunk_to_citation(c, bm25_tokens) for c in hits]
            extractive_answer_parts = [
                f"{c.text} [{i}]" for i, c in enumerate(hits, start=1)
            ]
            extractive_answer = "\n\n".join(extractive_answer_parts)
            conf = 'medium'
            if citations and all(c.status != 'current' for c in citations):
                conf = 'low'

            return AskResponse(
                answer=extractive_answer,
                answerable=True,
                confidence=conf,
                citations=citations,
                missing_info=None,
                expanded_terms=expanded_terms,
            )

        # 5. Process and validate LLM result
        raw_answer = str(llm_response.get('answer', '')).strip()
        raw_answerable = bool(llm_response.get('answerable', True))
        raw_confidence = str(llm_response.get('confidence', 'medium')).lower()
        if raw_confidence not in ['high', 'medium', 'low']:
            raw_confidence = 'medium'
        raw_used = llm_response.get('used_passages', [])
        missing_info = llm_response.get('missing_info')

        if not raw_answerable:
            return AskResponse(
                answer=raw_answer or "I do not have sufficient information in the accessible documents to answer this question.",
                answerable=False,
                confidence="low",
                citations=[],
                missing_info=missing_info or _build_missing_info(question),
                expanded_terms=expanded_terms,
            )

        # Collect passage numbers from answer text and used_passages
        # Match [1], [2], etc. in the answer text
        in_text_markers = [
            int(m) for m in re.findall(r'\[(\d+)\]', raw_answer)
            if 1 <= int(m) <= len(top_chunks)
        ]
        
        valid_used = [
            int(p) for p in raw_used
            if isinstance(p, (int, str)) and str(p).isdigit() and 1 <= int(p) <= len(top_chunks)
        ]

        # Determine order of citations
        seen = set()
        ordered_passages: list[int] = []
        for p in in_text_markers:
            if p not in seen:
                seen.add(p)
                ordered_passages.append(p)
        for p in valid_used:
            if p not in seen:
                seen.add(p)
                ordered_passages.append(p)

        if not ordered_passages:
            # Fallback to top chunk
            ordered_passages = [1]
            if not in_text_markers:
                raw_answer = f"{raw_answer} [1]"

        # Build citations and renumber markers
        # Map old passage number to new citation index 1..M
        passage_to_new_idx = {p: new_idx for new_idx, p in enumerate(ordered_passages, start=1)}
        citations = [
            _chunk_to_citation(top_chunks[p - 1], bm25_tokens)
            for p in ordered_passages
        ]

        # Renumber markers in raw_answer safely using unique tokens
        def replace_marker(match):
            old_num = int(match.group(1))
            new_num = passage_to_new_idx.get(old_num)
            if new_num is not None:
                return f"__CITE_{new_num}__"
            return match.group(0)

        renumbered = re.sub(r'\[(\d+)\]', replace_marker, raw_answer)
        final_answer = re.sub(r'__CITE_(\d+)__', r'[\1]', renumbered)

        final_confidence = raw_confidence
        # Set confidence low if every cited chunk is non-current
        if citations and all(c.status != 'current' for c in citations):
            final_confidence = 'low'

        return AskResponse(
            answer=final_answer,
            answerable=True,
            confidence=final_confidence,
            citations=citations,
            missing_info=missing_info if not raw_answerable else None,
            expanded_terms=expanded_terms,
        )

    except Exception as e:
        sys.stderr.write(f"[retrieval answer error] {e}\n")
        return AskResponse(
            answer="I do not have sufficient information in the accessible documents to answer this question.",
            answerable=False,
            confidence="low",
            citations=[],
            missing_info="An internal retrieval error occurred.",
            expanded_terms={},
        )
