from contracts import AskRequest, AskResponse, Chunk, Conflict, GapItem, Stats


def detect_conflicts(chunks: list[Chunk]) -> list[Conflict]:
    return []


def log_query(req: AskRequest, resp: AskResponse) -> None:
    return None


def gap_report() -> list[GapItem]:
    return [GapItem(question='How do I calibrate an HPLC column?', asked_count=1, last_asked='2026-10-13', reason='No source found')]


def get_stats() -> Stats:
    return Stats()
