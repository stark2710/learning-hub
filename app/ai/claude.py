import json
from urllib.request import urlopen, Request

from app.config import ANTHROPIC_API, SSL_CTX


class ClaudeClient:
    DEFAULT_MODEL = "claude-sonnet-4-6"

    @classmethod
    def complete(cls, api_key: str, messages: list, system: str,
                 max_tokens: int = 4096, model: str = "") -> str:
        req_body = json.dumps({
            "model": model or cls.DEFAULT_MODEL,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }).encode()
        req = Request(
            f"{ANTHROPIC_API}/v1/messages",
            data=req_body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urlopen(req, context=SSL_CTX, timeout=180) as resp:
            raw = json.loads(resp.read())
        return raw["content"][0]["text"]
