from app.integrations.ollama.protocols import LLMClient
from app.services.prompts.business_summary import build_business_summary_prompt

class BusinessInterpretationService:

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def generate_summary(self, ventas_mes: float, clientes: int) -> str:
        prompt = build_business_summary_prompt(ventas_mes, clientes)
        return self._llm_client.generate(prompt)

    @staticmethod
    def build_prompt(ventas_mes: float, clientes: int) -> str:
        return build_business_summary_prompt(ventas_mes, clientes)
