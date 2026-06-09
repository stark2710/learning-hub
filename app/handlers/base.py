import json
import mimetypes
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler

from app.config import BASE_DIR
from app.jobs import JobRegistry


class BaseHandler(BaseHTTPRequestHandler):

    # ── CORS / response helpers ───────────────────────────────────────────

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers",
                         "Content-Type, x-api-key, anthropic-version")

    def _error(self, code: int, msg: str):
        body = json.dumps({"error": msg}).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _json_ok(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length))

    # ── Job helper ────────────────────────────────────────────────────────

    def _start_job(self, target, extra_args: tuple) -> None:
        """Create a job, spin a daemon thread, and respond with 202 + job_id."""
        job_id = uuid.uuid4().hex[:8]
        JobRegistry.set(job_id, {"status": "running"})
        threading.Thread(target=target, args=(job_id,) + extra_args, daemon=True).start()
        self._json_ok({"job_id": job_id}, status=202)

    # ── Static file serving ───────────────────────────────────────────────

    def _serve_static(self):
        rel = self.path.split("?")[0].lstrip("/") or "index.html"
        path = os.path.normpath(os.path.join(BASE_DIR, rel))

        if not path.startswith(BASE_DIR):
            self._error(403, "Forbidden")
            return

        if os.path.isdir(path):
            path = os.path.join(path, "index.html")

        if not os.path.exists(path):
            self.send_response(404)
            self._cors()
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        mime, _ = mimetypes.guess_type(path)
        with open(path, "rb") as f:
            data = f.read()

        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", mime or "text/html")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        if args and str(args[1]) not in ("200", "204"):
            print(f"  [{args[1]}] {args[0]}")
