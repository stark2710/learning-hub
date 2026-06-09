from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from app.config import ANTHROPIC_API, OLLAMA_URL, SSL_CTX
from app.ai.ollama import OllamaClient


class ProxyHandlersMixin:

    def _proxy_anthropic(self):
        """Stream-proxy a request to the Anthropic API (for chat in lesson.html)."""
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        api_key = self.headers.get("x-api-key", "")

        req = Request(
            f"{ANTHROPIC_API}{self.path}",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        try:
            with urlopen(req, context=SSL_CTX) as resp:
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("X-Accel-Buffering", "no")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                while True:
                    chunk = resp.read(256)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except HTTPError as e:
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self._error(500, str(e))

    def _ollama_proxy(self, method: str, path: str, body):
        """Stream-proxy a request to the local Ollama server (auto-starts if needed)."""
        if not OllamaClient.ensure_running():
            self._error(503,
                "Ollama is not installed or could not be started. "
                "Install from https://ollama.com")
            return
        try:
            req = Request(f"{OLLAMA_URL}{path}", data=body, method=method)
            req.add_header("Content-Type", "application/json")
            with urlopen(req, timeout=120) as resp:
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type",
                                 resp.headers.get("Content-Type", "application/json"))
                self.end_headers()
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except URLError as e:
            self._error(502, f"Ollama error: {e}")
