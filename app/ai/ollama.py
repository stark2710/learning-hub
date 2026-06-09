import json
import shutil
import subprocess
import time
from urllib.request import urlopen, Request

from app.config import OLLAMA_URL


class OllamaClient:
    _proc = None  # subprocess handle if we started Ollama

    @classmethod
    def ensure_running(cls) -> bool:
        try:
            urlopen(f"{OLLAMA_URL}/api/tags", timeout=2)
            return True
        except Exception:
            pass

        if not shutil.which("ollama"):
            return False

        try:
            cls._proc = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            return False

        for _ in range(16):
            time.sleep(0.5)
            try:
                urlopen(f"{OLLAMA_URL}/api/tags", timeout=1)
                return True
            except Exception:
                pass

        return False

    @classmethod
    def complete(cls, model: str, messages: list, system: str, max_tokens: int = 4096) -> str:
        if not cls.ensure_running():
            raise RuntimeError("Ollama is not available")
        all_messages = [{"role": "system", "content": system}] + messages
        req_body = json.dumps({
            "model": model,
            "messages": all_messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "num_ctx": 16384,
            },
        }).encode()
        req = Request(f"{OLLAMA_URL}/api/chat", data=req_body,
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read())
        return data["message"]["content"]
