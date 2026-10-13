"""
corpus_gen/client.py
Tiny standalone Groq client for corpus generation.
Performs resilient LLM calls with timeout, retry, and fallback to fast model.
Never raises; returns empty string on any failure or when USE_MOCK_LLM=1.
"""

import os
import sys
import time
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model_main = os.getenv("GROQ_MODEL_MAIN", "llama-3.3-70b-versatile").strip()
        self.model_fast = os.getenv("GROQ_MODEL_FAST", "llama-3.1-8b-instant").strip()
        self.use_mock = os.getenv("USE_MOCK_LLM", "0").strip() == "1"
        self._client = None

    def _get_client(self):
        if self._client is None and self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key, timeout=20.0)
            except Exception as e:
                sys.stderr.write(f"[GroqClient] Failed to initialize client: {e}\n")
                self._client = None
        return self._client

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate completion text from prompt.
        Returns empty string immediately if USE_MOCK_LLM=1 or if API key is missing.
        Retries once after 2 seconds on 429 or 5xx, falling back to fast model.
        Never raises exceptions; returns empty string on failure.
        """
        if self.use_mock or not self.api_key:
            return ""

        client = self._get_client()
        if client is None:
            return ""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Primary attempt with main model
        try:
            response = client.chat.completions.create(
                model=self.model_main,
                messages=messages,
                temperature=0.2,
                max_completion_tokens=2048,
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except Exception as exc:
            # Check if status code is 429 or 5xx
            status_code = getattr(exc, "status_code", None)
            is_retryable = False
            if status_code is not None:
                if status_code == 429 or status_code >= 500:
                    is_retryable = True
            else:
                exc_str = str(exc).lower()
                if "429" in exc_str or "rate limit" in exc_str or "500" in exc_str or "503" in exc_str or "server error" in exc_str:
                    is_retryable = True

            if is_retryable:
                sys.stderr.write(f"[GroqClient] Received {status_code or 'error'}, retrying in 2s with fast model {self.model_fast}...\n")
                time.sleep(2)
                try:
                    response = client.chat.completions.create(
                        model=self.model_fast,
                        messages=messages,
                        temperature=0.2,
                        max_completion_tokens=2048,
                    )
                    content = response.choices[0].message.content or ""
                    return content.strip()
                except Exception as retry_exc:
                    sys.stderr.write(f"[GroqClient] Fallback retry failed: {retry_exc}\n")
                    return ""
            else:
                sys.stderr.write(f"[GroqClient] Call failed: {exc}\n")
                return ""


# Module-level client instance and helper function
_default_client = GroqClient()


def generate(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Convenience function calling the default Groq client."""
    return _default_client.generate(prompt, system_prompt=system_prompt)
