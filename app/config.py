import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
RAW_DIR = DATA / 'raw'
PROCESSED_DIR = DATA / 'processed'
FIXTURES_DIR = DATA / 'fixtures'
CACHE_DIR = DATA / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def raw_dir() -> Path:
    # Real corpus if Dev 1 has produced it, otherwise Dev 2's sample files.
    if any(RAW_DIR.rglob('*.meta.json')):
        return RAW_DIR
    return FIXTURES_DIR / 'raw_sample'


def chunks_path() -> Path:
    # Real chunks if built, otherwise the frozen fixture.
    real = PROCESSED_DIR / 'chunks.json'
    return real if real.exists() else FIXTURES_DIR / 'chunks_sample.json'


def use_mock_llm() -> bool:
    return os.getenv('USE_MOCK_LLM', '0') == '1'


def llm_mode() -> str:
    if use_mock_llm():
        return 'mock'
    return 'groq' if os.getenv('GROQ_API_KEY') else 'offline'
