import json
import os
import re
import shutil
import subprocess
import tempfile

from app.config import BASE_DIR, DEMO_MODE, TTS_VOICE
from app.jobs import JobRegistry
from app.tasks.generation import run_generate_lesson
from app.ai.local_claude import LocalClaudeClient

# espeak-ng voices offered when the macOS `say` binary is unavailable (Linux/Docker).
ESPEAK_VOICES = [("en-us", "en"), ("en-gb", "en"), ("hi", "hi")]


class MiscHandlersMixin:

    def _app_config(self):
        """Client-readable runtime config so the UI can hide disabled controls."""
        self._json_ok({"demo_mode": DEMO_MODE, "tts_enabled": True})

    def _generation_status(self):
        job_id = self.path.split("?job=", 1)[1] if "?job=" in self.path else ""
        self._json_ok(JobRegistry.get(job_id))

    def _local_claude_chat(self):
        try:
            body = self._read_body()
            messages = body.get("messages", [])
            system = body.get("system", "")
            model = body.get("claude_model", "")
            content = LocalClaudeClient.complete(messages, system, model=model)
            self._json_ok({"content": content})
        except Exception as e:
            self._error(500, str(e))

    def _generate_lesson(self):
        try:
            body = self._read_body()
            provider = body.get("provider", "claude")
            api_key = body.get("api_key", "")
            ollama_model = body.get("ollama_model", "")
            claude_model = body.get("claude_model", "")
            if provider not in ("ollama", "local-claude") and not api_key:
                self._error(400, "api_key required")
                return
            self._start_job(run_generate_lesson, (api_key, BASE_DIR, provider, ollama_model, claude_model))
        except Exception as e:
            self._error(500, str(e))

    def _mark_complete(self):
        try:
            body = self._read_body()
            lesson_id = body.get("lesson_id", "")
            progress_path = os.path.join(BASE_DIR, "progress.json")
            with open(progress_path) as f:
                progress = json.load(f)
            progress.setdefault("completed_lessons", {})
            if lesson_id in progress["completed_lessons"]:
                progress["completed_lessons"][lesson_id]["completed"] = True
            else:
                progress["completed_lessons"][lesson_id] = {"completed": True}
            with open(progress_path, "w") as f:
                json.dump(progress, f, indent=2)
            self._json_ok({"ok": True})
        except Exception as e:
            self._error(500, str(e))

    def _completed_lessons(self):
        try:
            progress_path = os.path.join(BASE_DIR, "progress.json")
            with open(progress_path) as f:
                progress = json.load(f)
            result = {
                lid: True
                for lid, data in progress.get("completed_lessons", {}).items()
                if data.get("completed")
            }
            self._json_ok(result)
        except Exception as e:
            self._error(500, str(e))

    def _content_map(self):
        content_dir = os.path.join(BASE_DIR, "content")
        mapping = {}
        for fn in os.listdir(content_dir):
            if fn.endswith(".md"):
                lesson_id = fn[:-3]
                if re.match(r"^m\d+-l\d+-", lesson_id):
                    m = re.match(r"(m\d+-l\d+)", lesson_id)
                else:
                    m = re.match(r"^(.+?-m\d+-l\d+)", lesson_id)
                if m:
                    mapping[m.group(1)] = lesson_id
        self._json_ok(mapping)

    def _log_question(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            entry = json.loads(self.rfile.read(length))
            log_path = os.path.join(BASE_DIR, "questions_log.json")
            log = []
            if os.path.exists(log_path):
                with open(log_path) as f:
                    log = json.load(f)
            log.append(entry)
            with open(log_path, "w") as f:
                json.dump(log, f, indent=2)
            self.send_response(200)
            self._cors()
            self.end_headers()
        except Exception as e:
            self._error(500, str(e))

    def _run_python(self):
        try:
            body = self._read_body()
            code = body.get("code", "")
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
                f.write(code)
                tmp_path = f.name
            try:
                result = subprocess.run(
                    ["python3", tmp_path], capture_output=True, text=True, timeout=10
                )
                response = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            except subprocess.TimeoutExpired:
                response = {"stdout": "", "stderr": "Execution timed out (10s limit)", "returncode": -1}
            finally:
                try: os.unlink(tmp_path)
                except: pass
            self._json_ok(response)
        except Exception as e:
            self._error(500, str(e))

    def _send_audio(self, data, content_type):
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_tts(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        text = body.get("text", "")
        voice = body.get("voice", TTS_VOICE)
        rate = body.get("rate", 175)

        if not text.strip():
            self.send_response(400)
            self._cors()
            self.end_headers()
            return

        if not shutil.which("say"):
            self._tts_espeak(text, voice, rate)
            return

        aiff_path = m4a_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
                aiff_path = f.name
            with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as f:
                m4a_path = f.name
            subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", aiff_path, text],
                           check=True, capture_output=True)
            subprocess.run(["afconvert", aiff_path, m4a_path, "-d", "aac", "-f", "m4af"],
                           check=True, capture_output=True)
            with open(m4a_path, "rb") as f:
                audio_data = f.read()
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "audio/mp4")
            self.send_header("Content-Length", str(len(audio_data)))
            self.end_headers()
            self.wfile.write(audio_data)
        except subprocess.CalledProcessError as e:
            self._error(500, f"TTS failed: {e.stderr.decode()}")
        except Exception as e:
            self._error(500, str(e))
        finally:
            for p in [aiff_path, m4a_path]:
                if p:
                    try: os.unlink(p)
                    except: pass

    def _tts_espeak(self, text, voice, rate):
        """Linux/Docker fallback TTS via espeak-ng. Returns a WAV blob."""
        if not shutil.which("espeak-ng"):
            self._error(501, "TTS unavailable: espeak-ng not installed")
            return
        if voice not in {v for v, _ in ESPEAK_VOICES}:
            voice = "en-us"
        try:
            rate = max(80, min(450, int(rate)))
        except (TypeError, ValueError):
            rate = 175
        wav_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wav_path = f.name
            subprocess.run(["espeak-ng", "-v", voice, "-s", str(rate), "-w", wav_path],
                           input=text, text=True, check=True, capture_output=True)
            with open(wav_path, "rb") as f:
                self._send_audio(f.read(), "audio/wav")
        except subprocess.CalledProcessError as e:
            self._error(500, f"TTS failed: {e.stderr}")
        except Exception as e:
            self._error(500, str(e))
        finally:
            if wav_path:
                try: os.unlink(wav_path)
                except: pass

    def _list_voices(self):
        if not shutil.which("say"):
            self._json_ok([{"name": n, "lang": l} for n, l in ESPEAK_VOICES])
            return
        try:
            result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
            indian = []
            for line in result.stdout.strip().split("\n"):
                if any(x in line for x in ["en_IN", "hi_IN", "ta_IN", "Rishi", "Lekha", "Vani"]):
                    parts = line.split()
                    indian.append({"name": parts[0], "lang": parts[1] if len(parts) > 1 else ""})
            self._json_ok(indian)
        except Exception as e:
            self._error(500, str(e))
