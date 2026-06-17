from typing import Any
from app.integrations.ollama.protocols import LLMClient
from app.services.context_fusion_service import FusedContext
from app.services.prompts.ai_response import build_ai_response_prompt
from app.services.prompts.business_analyst import build_business_analyst_prompt
from app.services.prompts.document_response import build_document_response_prompt
from app.services.prompts.hybrid_response import build_hybrid_response_prompt

class AIResponseService:

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def generate(self, question: str, intent: str, data: dict[str, Any] | list[dict[str, Any]] | None) -> str:
        prompt = build_ai_response_prompt(question=question, intent=intent, data=data)
        return self._llm_client.generate(prompt)

    def generate_from_documents(self, question: str, results: list[dict[str, Any]]) -> str:
        prompt = build_document_response_prompt(question=question, results=results)
        return self._llm_client.generate(prompt)

    def generate_hybrid(self, question: str, context: FusedContext) -> str:
        prompt = build_hybrid_response_prompt(question=question, context=context)
        return self._llm_client.generate(prompt)

    def generate_business_analysis(self, question: str, snapshot: dict[str, Any]) -> str:
        prompt = build_business_analyst_prompt(question=question, snapshot=snapshot)
        return self._llm_client.generate(prompt)

    @staticmethod
    def build_prompt(question: str, intent: str, data: dict[str, Any] | list[dict[str, Any]] | None) -> str:
        return build_ai_response_prompt(question=question, intent=intent, data=data)

    @staticmethod
    def build_document_prompt(question: str, results: list[dict[str, Any]]) -> str:
        return build_document_response_prompt(question=question, results=results)

    @staticmethod
    def build_hybrid_prompt(question: str, context: FusedContext) -> str:
        return build_hybrid_response_prompt(question=question, context=context)

    @staticmethod
    def build_business_analysis_prompt(question: str, snapshot: dict[str, Any]) -> str:
        return build_business_analyst_prompt(question=question, snapshot=snapshot)
