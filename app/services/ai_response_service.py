from typing import Any
from app.integrations.ollama.protocols import LLMClient
from app.services.prompts.ai_response import build_ai_response_prompt

class AIResponseService:

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def generate(self, question: str, intent: str, data: dict[str, Any] | list[dict[str, Any]] | None) -> str:
        prompt = build_ai_response_prompt(question=question, intent=intent, data=data)
        return self._llm_client.generate(prompt)

    @staticmethod
    def build_prompt(question: str, intent: str, data: dict[str, Any] | list[dict[str, Any]] | None) -> str:
        return build_ai_response_prompt(question=question, intent=intent, data=data)
