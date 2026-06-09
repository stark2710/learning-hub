from app.config import BASE_DIR
from app.tasks.curriculum import run_add_domain, run_add_module, run_add_lesson
from app.tasks.generation import run_generate_first_domain_lesson, run_generate_next_domain_lesson


class CurriculumHandlersMixin:

    def _ai_params(self, body: dict) -> tuple:
        return (
            body.get("provider", "claude"),
            body.get("api_key", ""),
            body.get("ollama_model", ""),
            body.get("claude_model", ""),
        )

    def _check_ai_key(self, provider: str, api_key: str) -> bool:
        if provider not in ("ollama", "local-claude") and not api_key:
            self._error(400, "api_key required")
            return False
        return True

    def _add_domain(self):
        try:
            body = self._read_body()
            provider, api_key, ollama_model, claude_model = self._ai_params(body)
            program_id = body.get("program_id", "")
            prompt = body.get("prompt", "")
            if not self._check_ai_key(provider, api_key):
                return
            if not all([program_id, prompt]):
                self._error(400, "program_id, prompt required")
                return
            self._start_job(run_add_domain,
                            (program_id, prompt, api_key, BASE_DIR, provider, ollama_model, claude_model))
        except Exception as e:
            self._error(500, str(e))

    def _add_module(self):
        try:
            body = self._read_body()
            provider, api_key, ollama_model, claude_model = self._ai_params(body)
            program_id = body.get("program_id", "") or body.get("target", "")
            domain_id = body.get("domain_id", "")
            prompt = body.get("prompt", "")
            if not self._check_ai_key(provider, api_key):
                return
            if not all([program_id, domain_id, prompt]):
                self._error(400, "program_id, domain_id, prompt required")
                return
            self._start_job(run_add_module,
                            (program_id, domain_id, prompt, api_key, BASE_DIR, provider, ollama_model, claude_model))
        except Exception as e:
            self._error(500, str(e))

    def _add_lesson(self):
        try:
            body = self._read_body()
            provider, api_key, ollama_model, claude_model = self._ai_params(body)
            program_id = body.get("program_id", "")
            domain_id = body.get("domain_id", "")
            mod_num = int(body.get("mod_num", 0))
            prompt = body.get("prompt", "")
            if not self._check_ai_key(provider, api_key):
                return
            if not all([program_id, domain_id, mod_num, prompt]):
                self._error(400, "program_id, domain_id, mod_num, prompt required")
                return
            self._start_job(run_add_lesson,
                            (program_id, domain_id, mod_num, prompt, api_key, BASE_DIR, provider, ollama_model, claude_model))
        except Exception as e:
            self._error(500, str(e))

    def _generate_first_domain_lesson(self):
        try:
            body = self._read_body()
            provider, api_key, ollama_model, claude_model = self._ai_params(body)
            program_id = body.get("program_id", "")
            domain_id = body.get("domain_id", "")
            if not self._check_ai_key(provider, api_key):
                return
            if not all([program_id, domain_id]):
                self._error(400, "program_id, domain_id required")
                return
            self._start_job(run_generate_first_domain_lesson,
                            (program_id, domain_id, api_key, BASE_DIR, provider, ollama_model, claude_model))
        except Exception as e:
            self._error(500, str(e))

    def _generate_next_domain_lesson(self):
        try:
            body = self._read_body()
            provider, api_key, ollama_model, claude_model = self._ai_params(body)
            program_id = body.get("program_id", "")
            domain_id = body.get("domain_id", "")
            current_lesson_key = body.get("current_lesson_key", "")
            if not self._check_ai_key(provider, api_key):
                return
            if not all([program_id, domain_id, current_lesson_key]):
                self._error(400, "program_id, domain_id, current_lesson_key required")
                return
            self._start_job(run_generate_next_domain_lesson,
                            (program_id, domain_id, current_lesson_key, api_key, BASE_DIR, provider, ollama_model, claude_model))
        except Exception as e:
            self._error(500, str(e))
