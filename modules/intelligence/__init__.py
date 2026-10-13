from contracts import AskRequest, AskResponse, Chunk, Conflict, GapItem, Stats
from modules.intelligence.conflicts import detect_conflicts
from modules.intelligence.gaps import log_query, gap_report, get_stats

__all__ = [
    'detect_conflicts',
    'log_query',
    'gap_report',
    'get_stats',
]
