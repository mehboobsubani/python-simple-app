"""Small client for the local Ollama HTTP API."""

import json
import os
from urllib import error, request


class OllamaError(RuntimeError):
    """Raised when Ollama cannot answer a request."""


def generate(prompt: str) -> str:
    """Generate a response using the configured local Ollama model."""
    base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    http_request = request.Request(
        f"{base_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=float(os.getenv("OLLAMA_TIMEOUT", "60"))) as response:
            result = json.loads(response.read())
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OllamaError(f"Ollama request failed: {exc}") from exc

    answer = result.get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise OllamaError("Ollama returned an empty response")
    return answer.strip()
