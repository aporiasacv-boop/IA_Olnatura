"""
Factory del cliente Ollama.

Centraliza la construcción del cliente a partir de Settings.
"""

from app.core.config import settings
from app.integrations.ollama.client import OllamaClient, OllamaClientConfig


def create_ollama_client() -> OllamaClient:
    """
    Crea una instancia del cliente Ollama usando la configuración global.

    Returns:
        Cliente Ollama listo para generar respuestas.
    """
    return OllamaClient(
        OllamaClientConfig(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.OLLAMA_REQUEST_TIMEOUT,
        )
    )
