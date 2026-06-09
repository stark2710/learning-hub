import os
import ssl

PORT = int(os.environ.get("PORT", "3131"))
HOST = os.environ.get("HOST", "127.0.0.1")
DEMO_MODE = os.environ.get("DEMO_MODE", "").strip().lower() in ("1", "true", "yes", "on")
ANTHROPIC_API = "https://api.anthropic.com"
TTS_VOICE = "Lekha"
OLLAMA_URL = "http://localhost:11434"
SSL_CTX = ssl._create_unverified_context()

# Absolute path to the project root (learning/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
