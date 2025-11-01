"""Client for interacting with a local Ollama instance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generator
import json

import requests


_TIMEOUT = (5, 120)


@dataclass
class LlmClient:
    """Simple HTTP client for Ollama."""

    host: str
    model: str

    def _url(self) -> str:
        return self.host.rstrip("/") + "/api/generate"

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        """Return the full completion for ``prompt``."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        response = requests.post(self._url(), json=payload, timeout=_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return (data.get("response") or "").strip()

    def stream(self, prompt: str, max_tokens: int = 256) -> Generator[str, None, None]:
        """Yield chunks from the streamed response."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {"num_predict": max_tokens},
        }
        with requests.post(self._url(), json=payload, timeout=_TIMEOUT, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:  # pragma: no cover - defensive
                    continue
                text = chunk.get("response")
                if text:
                    yield text
                if chunk.get("done"):
                    break
