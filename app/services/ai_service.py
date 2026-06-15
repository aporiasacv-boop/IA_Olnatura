"""
Servicio de inteligencia artificial con Ollama.
"""

from app.integrations.ollama.protocols import LLMClient


class AIService:
    """Orquesta inferencia de lenguaje natural mediante Ollama."""

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def test_prompt(self, prompt: str) -> str:
        """
        Envía un prompt de prueba al modelo y retorna su respuesta.

        Args:
            prompt: Texto de entrada.

        Returns:
            Respuesta generada por el modelo.
        """
        return self._llm_client.generate(prompt)
