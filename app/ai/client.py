from .claude import ClaudeClient
from .ollama import OllamaClient
from .local_claude import LocalClaudeClient


class AIClient:
    @staticmethod
    def complete(provider: str, api_key: str, ollama_model: str,
                 messages: list, system: str,
                 max_tokens: int = 4096, claude_model: str = "",
                 timeout: int = 900) -> str:
        # timeout default is generous (900s): lesson generation via the local
        # `claude` CLI legitimately runs ~8 min on the full prompt. Short-response
        # chat calls go through LocalClaudeClient.complete directly (300s default).
        if provider == "local-claude":
            return LocalClaudeClient.complete(messages, system, max_tokens, claude_model, timeout)
        if provider == "ollama":
            return OllamaClient.complete(ollama_model, messages, system, max_tokens)
        return ClaudeClient.complete(api_key, messages, system, max_tokens, claude_model)
