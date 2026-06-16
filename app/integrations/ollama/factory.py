from app.core.config import settings
from app.integrations.ollama.client import OllamaClient, OllamaClientConfig

def create_ollama_client() -> OllamaClient:
    return OllamaClient(OllamaClientConfig(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL, timeout=settings.OLLAMA_REQUEST_TIMEOUT))
