import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from typing import Optional

from app import config


def _hash_key(model: str, system: str, prompt: str) -> str:
    raw = f"{model}\n{system}\n{prompt}".encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def _get_db():
    db_path = config.CACHE_DIR / 'llm.sqlite'
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
    return conn


def _cache_get(key: str) -> Optional[str]:
    try:
        with _get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM llm_cache WHERE key = ?", (key,))
            row = cur.fetchone()
            if row:
                return row[0]
    except Exception as e:
        sys.stderr.write(f"[llm cache error] {e}\n")
    return None


def _cache_set(key: str, value: str):
    if not value or not value.strip():
        return
    try:
        with _get_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO llm_cache (key, value, created_at) VALUES (?, ?, ?)",
                (key, value, time.time())
            )
    except Exception as e:
        sys.stderr.write(f"[llm cache set error] {e}\n")


def _parse_json_safely(text: str) -> dict:
    if not text or not text.strip():
        return {}
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean)
        clean = clean.strip()
    try:
        data = json.loads(clean)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        start = clean.find("{")
        end = clean.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(clean[start : end + 1])
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {}


def _call_groq_with_retry(api_key: str, model: str, prompt: str, system: str, is_json: bool) -> str:
    try:
        from groq import Groq, APIStatusError, APITimeoutError
    except ImportError:
        sys.stderr.write("[llm] groq SDK not installed\n")
        return ""

    for attempt in range(2):
        try:
            client = Groq(api_key=api_key, timeout=20.0)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            
            # Groq JSON mode requires the word 'json' in messages
            user_content = prompt
            if is_json and "json" not in user_content.lower() and "json" not in (system or "").lower():
                user_content = f"{user_content}\n\nPlease respond in valid JSON format."

            messages.append({"role": "user", "content": user_content})

            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.0,
            }
            if is_json:
                kwargs["response_format"] = {"type": "json_object"}

            sys.stderr.write(f"[llm] Calling Groq model {model} (attempt {attempt + 1})\n")
            completion = client.chat.completions.create(**kwargs)
            res = completion.choices[0].message.content or ""
            return res
        except (APIStatusError, APITimeoutError, Exception) as e:
            status_code = getattr(e, 'status_code', None)
            is_timeout = isinstance(e, APITimeoutError) or "timeout" in str(e).lower()
            is_retryable = is_timeout or (status_code is not None and (status_code == 429 or status_code >= 500))
            sys.stderr.write(f"[llm] Groq error on {model} (attempt {attempt + 1}): {type(e).__name__} {status_code or ''}\n")
            if attempt == 0 and is_retryable:
                time.sleep(2.0)
                continue
            break
    return ""


def _call_gemini_with_retry(api_key: str, model: str, prompt: str, system: str, is_json: bool) -> str:
    try:
        import requests
    except ImportError:
        sys.stderr.write("[llm] requests not installed\n")
        return ""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": system}]})
        contents.append({"role": "model", "parts": [{"text": "Understood."}]})
    
    user_text = prompt
    if is_json and "json" not in user_text.lower():
        user_text = f"{user_text}\n\nReturn output in valid JSON."
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.0,
        }
    }
    if is_json:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    for attempt in range(2):
        try:
            sys.stderr.write(f"[llm] Calling Gemini {model} (attempt {attempt + 1})\n")
            resp = requests.post(url, json=payload, timeout=20.0)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
            status_code = resp.status_code
            is_retryable = (status_code == 429 or status_code >= 500)
            sys.stderr.write(f"[llm] Gemini error {status_code} (attempt {attempt + 1})\n")
            if attempt == 0 and is_retryable:
                time.sleep(2.0)
                continue
            break
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"[llm] Gemini request error: {type(e).__name__}\n")
            if attempt == 0:
                time.sleep(2.0)
                continue
            break
        except Exception as e:
            sys.stderr.write(f"[llm] Gemini error: {type(e).__name__}\n")
            break
    return ""


def complete_text(prompt: str, system: str = '') -> str:
    groq_main = os.getenv('GROQ_MODEL_MAIN') or 'llama-3.3-70b-versatile'
    groq_fast = os.getenv('GROQ_MODEL_FAST') or 'llama-3.1-8b-instant'
    gemini_model = 'gemini-1.5-flash'

    # 1. Cache lookup
    for model in [groq_main, groq_fast, gemini_model]:
        k = _hash_key(model, system, prompt)
        cached = _cache_get(k)
        if cached is not None and cached.strip():
            sys.stderr.write(f"[llm] Cache hit for model {model}\n")
            return cached

    sys.stderr.write("[llm] Cache miss\n")

    # 2. Mock check
    if config.use_mock_llm():
        sys.stderr.write("[llm] Mock LLM active, returning empty string\n")
        return ''

    # 3. Groq main model
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key and groq_main:
        res = _call_groq_with_retry(groq_key, groq_main, prompt, system, is_json=False)
        if res and res.strip():
            _cache_set(_hash_key(groq_main, system, prompt), res)
            return res

    # 4. Groq fast model
    if groq_key and groq_fast:
        res = _call_groq_with_retry(groq_key, groq_fast, prompt, system, is_json=False)
        if res and res.strip():
            _cache_set(_hash_key(groq_fast, system, prompt), res)
            return res

    # 5. Gemini fallback
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        res = _call_gemini_with_retry(gemini_key, gemini_model, prompt, system, is_json=False)
        if res and res.strip():
            _cache_set(_hash_key(gemini_model, system, prompt), res)
            return res

    # 6. Fallback
    return ''


def complete_json(prompt: str, system: str = '') -> dict:
    groq_main = os.getenv('GROQ_MODEL_MAIN') or 'llama-3.3-70b-versatile'
    groq_fast = os.getenv('GROQ_MODEL_FAST') or 'llama-3.1-8b-instant'
    gemini_model = 'gemini-1.5-flash'

    # 1. Cache lookup
    for model in [groq_main, groq_fast, gemini_model]:
        k = _hash_key(model, system, prompt)
        cached = _cache_get(k)
        if cached is not None and cached.strip():
            parsed = _parse_json_safely(cached)
            if parsed:
                sys.stderr.write(f"[llm] Cache hit for JSON model {model}\n")
                return parsed

    sys.stderr.write("[llm] Cache miss for JSON\n")

    # 2. Mock check
    if config.use_mock_llm():
        sys.stderr.write("[llm] Mock LLM active, returning empty dict\n")
        return {}

    # 3. Groq main model
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key and groq_main:
        res = _call_groq_with_retry(groq_key, groq_main, prompt, system, is_json=True)
        if res:
            parsed = _parse_json_safely(res)
            if parsed:
                _cache_set(_hash_key(groq_main, system, prompt), json.dumps(parsed))
                return parsed

    # 4. Groq fast model
    if groq_key and groq_fast:
        res = _call_groq_with_retry(groq_key, groq_fast, prompt, system, is_json=True)
        if res:
            parsed = _parse_json_safely(res)
            if parsed:
                _cache_set(_hash_key(groq_fast, system, prompt), json.dumps(parsed))
                return parsed

    # 5. Gemini fallback
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        res = _call_gemini_with_retry(gemini_key, gemini_model, prompt, system, is_json=True)
        if res:
            parsed = _parse_json_safely(res)
            if parsed:
                _cache_set(_hash_key(gemini_model, system, prompt), json.dumps(parsed))
                return parsed

    # 6. Fallback
    return {}
