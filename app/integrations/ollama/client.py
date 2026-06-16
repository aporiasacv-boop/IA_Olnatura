from dataclasses import dataclass
import httpx
from app.integrations.ollama.exceptions import OllamaAPIError, OllamaConnectionError

@dataclass(frozen=True)
class OllamaClientConfig:
    base_url: str
    model: str
    timeout: float = 60.0

class OllamaClient:

    def __init__(self, config: OllamaClientConfig, http_client: httpx.Client | None=None):
        self._config = config
        self._http_client = http_client or httpx.Client(timeout=config.timeout)

    def generate(self, prompt: str) -> str:
        url = f"{self._config.base_url.rstrip('/')}/api/generate"
        payload = {'model': self._config.model, 'prompt': prompt, 'stream': False}
        try:
            response = self._http_client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise OllamaConnectionError(f'No se pudo conectar con Ollama: {exc}') from exc
        if response.status_code != 200:
            raise OllamaAPIError(f'Error Ollama {response.status_code}: {response.text}', status_code=response.status_code)
        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaAPIError('La respuesta de Ollama no es JSON válido') from exc
        model_response = data.get('response')
        if model_response is None:
            raise OllamaAPIError("La respuesta de Ollama no incluye el campo 'response'")
        return str(model_response)
