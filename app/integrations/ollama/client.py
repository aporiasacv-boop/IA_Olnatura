"""
Cliente HTTP para Ollama.

Consume la API /api/generate para inferencia con modelos locales.
"""

from dataclasses import dataclass

import httpx

from app.integrations.ollama.exceptions import OllamaAPIError, OllamaConnectionError


@dataclass(frozen=True)
class OllamaClientConfig:
    """Parámetros de conexión con Ollama."""

    base_url: str
    model: str
    timeout: float = 60.0


class OllamaClient:
    """
    Cliente desacoplado para Ollama.

    Envía prompts al endpoint /api/generate y retorna la respuesta del modelo.
    """

    def __init__(
        self,
        config: OllamaClientConfig,
        http_client: httpx.Client | None = None,
    ):
        self._config = config
        self._http_client = http_client or httpx.Client(timeout=config.timeout)

    def generate(self, prompt: str) -> str:
        """
        Genera texto usando el modelo configurado en Ollama.

        Args:
            prompt: Texto de entrada.

        Returns:
            Respuesta generada por el modelo.

        Raises:
            OllamaConnectionError: Error de red o timeout.
            OllamaAPIError: Respuesta HTTP no exitosa o JSON inválido.
        """
        url = f"{self._config.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self._config.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = self._http_client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise OllamaConnectionError(
                f"No se pudo conectar con Ollama: {exc}"
            ) from exc

        if response.status_code != 200:
            raise OllamaAPIError(
                f"Error Ollama {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaAPIError("La respuesta de Ollama no es JSON válido") from exc

        model_response = data.get("response")
        if model_response is None:
            raise OllamaAPIError("La respuesta de Ollama no incluye el campo 'response'")

        return str(model_response)
