import shutil
import subprocess


class LocalClaudeClient:
    DEFAULT_MODEL = "claude-sonnet-4-6"

    @classmethod
    def complete(cls, messages: list, system: str,
                 max_tokens: int = 8192, model: str = "", timeout: int = 300) -> str:
        if not shutil.which("claude"):
            raise RuntimeError("claude CLI not found in PATH")
        user_content = messages[-1]["content"] if messages else ""
        cmd = [
            "claude", "-p", user_content,
            "--system-prompt", system,
            "--model", model or cls.DEFAULT_MODEL,
            "--no-session-persistence",
            "--output-format", "text",
            "--tools", "",
            "--disable-slash-commands",
            "--strict-mcp-config",  # no --mcp-config => skip spawning/health-checking all MCP servers (we use no tools)
        ]
        # stdin=DEVNULL so `claude -p` never blocks waiting on inherited stdin.
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=timeout, stdin=subprocess.DEVNULL)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "claude CLI returned non-zero exit")
        return result.stdout.strip()
