"""
Contratos del cliente Ollama.

Permite inyectar implementaciones mock en pruebas
sin acoplar servicios al cliente HTTP concreto.
"""

from typing import Protocol


class LLMClient(Protocol):
    """Contrato mínimo para clientes de modelos de lenguaje."""

    def generate(self, prompt: str) -> str:
        """
        Genera una respuesta a partir de un prompt de texto.

        Args:
            prompt: Texto de entrada para el modelo.

        Returns:
            Texto generado por el modelo.

        Raises:
            OllamaError: Si la generación falla.
        """
        ...
