from app.config import DEMO_MODE
from .base import BaseHandler
from .programs import ProgramHandlersMixin
from .curriculum import CurriculumHandlersMixin
from .proxy import ProxyHandlersMixin
from .misc import MiscHandlersMixin

# Routes that mutate the server or execute code — disabled when DEMO_MODE is on.
DEMO_BLOCKED = {
    "/run_python",
    "/generate_lesson",
    "/create_program",
    "/add_domain",
    "/add_module",
    "/add_lesson",
    "/generate_first_domain_lesson",
    "/generate_next_domain_lesson",
    "/local_claude_chat",
}


class ProxyHandler(
    MiscHandlersMixin,
    CurriculumHandlersMixin,
    ProgramHandlersMixin,
    ProxyHandlersMixin,
    BaseHandler,
):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        p = self.path
        if p == "/tts/voices":
            self._list_voices()
        elif p.startswith("/generation_status"):
            self._generation_status()
        elif p == "/content_map":
            self._content_map()
        elif p == "/completed_lessons":
            self._completed_lessons()
        elif p == "/programs":
            self._list_programs()
        elif p.startswith("/program/"):
            self._get_program()
        elif p == "/app_config":
            self._app_config()
        elif p == "/ollama/tags":
            self._ollama_proxy("GET", "/api/tags", None)
        else:
            self._serve_static()

    def do_POST(self):
        p = self.path
        if DEMO_MODE and p in DEMO_BLOCKED:
            self._error(403, "This action is disabled in the public demo.")
            return
        if p == "/tts":
            self._handle_tts()
        elif p == "/log_question":
            self._log_question()
        elif p == "/run_python":
            self._run_python()
        elif p == "/mark_complete":
            self._mark_complete()
        elif p == "/local_claude_chat":
            self._local_claude_chat()
        elif p == "/generate_lesson":
            self._generate_lesson()
        elif p == "/create_program":
            self._create_program()
        elif p == "/add_domain":
            self._add_domain()
        elif p == "/add_module":
            self._add_module()
        elif p == "/add_lesson":
            self._add_lesson()
        elif p == "/generate_first_domain_lesson":
            self._generate_first_domain_lesson()
        elif p == "/generate_next_domain_lesson":
            self._generate_next_domain_lesson()
        elif p == "/ollama/chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            self._ollama_proxy("POST", "/api/chat", body)
        else:
            self._proxy_anthropic()
