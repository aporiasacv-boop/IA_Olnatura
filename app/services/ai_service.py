from app.integrations.ollama.protocols import LLMClient

class AIService:

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def test_prompt(self, prompt: str) -> str:
        return self._llm_client.generate(prompt)
