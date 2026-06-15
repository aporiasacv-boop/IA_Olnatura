"""
Pruebas del cliente Ollama.
"""

from unittest.mock import MagicMock

import httpx
import pytest

from app.integrations.ollama.client import OllamaClient, OllamaClientConfig
from app.integrations.ollama.exceptions import OllamaAPIError, OllamaConnectionError


@pytest.fixture
def ollama_config() -> OllamaClientConfig:
    return OllamaClientConfig(
        base_url="http://localhost:11434",
        model="llama3.2",
        timeout=30.0,
    )


def test_generate_returns_model_response(ollama_config: OllamaClientConfig) -> None:
    """Verifica generación exitosa de respuesta."""
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 200
    http_response.json.return_value = {
        "model": "llama3.2",
        "response": "¡Hola! ¿En qué puedo ayudarte?",
        "done": True,
    }
    http_client.post.return_value = http_response

    client = OllamaClient(ollama_config, http_client=http_client)
    result = client.generate("Hola")

    assert result == "¡Hola! ¿En qué puedo ayudarte?"
    http_client.post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": "Hola",
            "stream": False,
        },
    )


def test_generate_raises_api_error_on_http_failure(ollama_config: OllamaClientConfig) -> None:
    """Verifica error API ante respuesta HTTP 500."""
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 500
    http_response.text = "Internal Server Error"
    http_client.post.return_value = http_response

    client = OllamaClient(ollama_config, http_client=http_client)

    with pytest.raises(OllamaAPIError, match="Error Ollama 500"):
        client.generate("Hola")


def test_generate_raises_connection_error_on_network_failure(
    ollama_config: OllamaClientConfig,
) -> None:
    """Verifica error de conexión ante fallo de red."""
    http_client = MagicMock()
    http_client.post.side_effect = httpx.ConnectError("Connection refused")

    client = OllamaClient(ollama_config, http_client=http_client)

    with pytest.raises(OllamaConnectionError, match="No se pudo conectar"):
        client.generate("Hola")


def test_generate_raises_api_error_when_response_missing(
    ollama_config: OllamaClientConfig,
) -> None:
    """Verifica error cuando la respuesta no incluye el campo response."""
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 200
    http_response.json.return_value = {"done": True}
    http_client.post.return_value = http_response

    client = OllamaClient(ollama_config, http_client=http_client)

    with pytest.raises(OllamaAPIError, match="no incluye el campo 'response'"):
        client.generate("Hola")
