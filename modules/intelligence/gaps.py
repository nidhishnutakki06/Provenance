import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from contracts import AskRequest, AskResponse, GapItem, Stats
from app import config

STOPWORDS = {
    'a', 'about', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'can', 'did', 'do',
    'does', 'for', 'from', 'how', 'i', 'in', 'is', 'it', 'of', 'on', 'or', 'should',
    'that', 'the', 'this', 'to', 'what', 'when', 'where', 'which', 'who', 'why',
    'will', 'with', 'would'
}


def _get_db_path(db_path: Optional[Path] = None) -> Path:
    if db_path is not None:
        return Path(db_path)
    return config.CACHE_DIR / 'queries.sqlite'


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            role TEXT NOT NULL,
            question TEXT NOT NULL,
            answerable INTEGER NOT NULL,
            confidence TEXT NOT NULL,
            minutes_saved REAL NOT NULL,
            n_citations INTEGER NOT NULL,
            n_conflicts INTEGER NOT NULL,
            reason TEXT
        );"""
    )
    conn.commit()


def log_query(req: AskRequest, resp: AskResponse, db_path: Optional[Path] = None) -> None:
    """Log an ask request and response to queries.sqlite. Never raises."""
    try:
        path = _get_db_path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        try:
            _init_db(conn)
            ts = datetime.now(timezone.utc).isoformat()
            answerable_val = 1 if resp.answerable else 0
            reason = resp.missing_info or ""
            if not reason and not resp.answerable:
                reason = "No source found"
            conn.execute(
                """INSERT INTO queries (ts, role, question, answerable, confidence, minutes_saved, n_citations, n_conflicts, reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ts,
                    req.role,
                    req.question,
                    answerable_val,
                    resp.confidence,
                    float(resp.minutes_saved),
                    len(resp.citations),
                    len(resp.conflicts),
                    reason,
                )
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"Error logging query to sqlite: {e}", file=sys.stderr)


def _tokenize(text: str) -> set[str]:
    """Lowercase, strip punctuation and stopwords, return token set."""
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    meaningful = {w for w in words if w not in STOPWORDS}
    return meaningful if meaningful else set(words)


def _jaccard(tokens_a: set[str], tokens_b: set[str]) -> float:
    if not tokens_a and not tokens_b:
        return 1.0
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return len(tokens_a & tokens_b) / len(union)


def gap_report(db_path: Optional[Path] = None) -> list[GapItem]:
    """Group unanswered or low-confidence queries by question similarity (Jaccard >= 0.6).

    Sorted by asked_count descending, then recency descending.
    """
    try:
        path = _get_db_path(db_path)
        if not path.exists():
            return []

        conn = sqlite3.connect(path)
        try:
            _init_db(conn)
            cursor = conn.execute(
                """SELECT question, ts, reason FROM queries
                   WHERE answerable = 0 OR confidence = 'low'
                   ORDER BY ts ASC"""
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        if not rows:
            return []

        # Cluster by token Jaccard similarity >= 0.6
        clusters: list[dict] = []
        for question, ts, reason in rows:
            tokens = _tokenize(question)
            matched_cluster = None
            for c in clusters:
                if _jaccard(tokens, c["tokens"]) >= 0.6:
                    matched_cluster = c
                    break

            if matched_cluster:
                matched_cluster["asked_count"] += 1
                if ts > matched_cluster["last_asked"]:
                    matched_cluster["last_asked"] = ts
                if reason and not matched_cluster["reason"]:
                    matched_cluster["reason"] = reason
            else:
                clusters.append({
                    "question": question,
                    "tokens": tokens,
                    "asked_count": 1,
                    "last_asked": ts,
                    "reason": reason or "No source found",
                })

        # Sort by count descending, then last_asked descending
        clusters.sort(key=lambda c: (c["asked_count"], c["last_asked"]), reverse=True)

        return [
            GapItem(
                question=c["question"],
                asked_count=c["asked_count"],
                last_asked=c["last_asked"][:10],  # YYYY-MM-DD
                reason=c["reason"],
            )
            for c in clusters
        ]

    except Exception as e:
        print(f"Error in gap_report: {e}", file=sys.stderr)
        return []


def get_stats(db_path: Optional[Path] = None) -> Stats:
    """Return aggregated metrics from the queries table."""
    try:
        path = _get_db_path(db_path)
        if not path.exists():
            return Stats()

        conn = sqlite3.connect(path)
        try:
            _init_db(conn)
            cursor = conn.execute(
                """SELECT 
                    COUNT(*),
                    COALESCE(SUM(CASE WHEN answerable = 1 THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN answerable = 0 THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(minutes_saved), 0.0),
                    COALESCE(SUM(n_conflicts), 0)
                   FROM queries"""
            )
            row = cursor.fetchone()
            total_questions = row[0] if row else 0
            answered = row[1] if row else 0
            unanswered = row[2] if row else 0
            total_minutes = round(row[3], 1) if row else 0.0
            conflicts_flagged = row[4] if row else 0

            cursor = conn.execute("SELECT role, COUNT(*) FROM queries GROUP BY role")
            by_role = {role: count for role, count in cursor.fetchall()}
        finally:
            conn.close()

        return Stats(
            total_questions=total_questions,
            answered=answered,
            unanswered=unanswered,
            total_minutes_saved=total_minutes,
            conflicts_flagged=conflicts_flagged,
            by_role=by_role,
        )

    except Exception as e:
        print(f"Error in get_stats: {e}", file=sys.stderr)
        return Stats()
