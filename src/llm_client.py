from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class LLMRequest:
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    extra: Optional[Dict[str, Any]] = None


class LLMClient:
    def __init__(
        self,
        api_base: str,
        api_key: str,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
        timeout_s: int = 60,
    ) -> None:
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.timeout_s = timeout_s

    def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            req = Request(url, data=data, headers=headers, method="POST")
            try:
                with urlopen(req, timeout=self.timeout_s) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except HTTPError as exc:
                body = exc.read().decode("utf-8") if exc.fp else ""
                raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
            except (URLError, ConnectionError) as exc:
                last_error = exc
            except Exception as exc:
                last_error = exc
            if attempt < self.max_retries:
                time.sleep(self.retry_backoff * (attempt + 1))
        raise RuntimeError(f"Network error after retries: {last_error}") from last_error

    def chat(self, request: LLMRequest) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = int(request.max_tokens)
        if request.extra:
            payload.update(request.extra)
        url = f"{self.api_base}/chat/completions"
        return self._post_json(url, payload)

    @staticmethod
    def extract_text(response: Dict[str, Any]) -> str:
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")
