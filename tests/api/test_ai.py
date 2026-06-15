"""
Pruebas del endpoint POST /ai/test.
"""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.deps import get_ai_service
from app.integrations.ollama.exceptions import OllamaConnectionError
from app.main import app
from app.services.ai_service import AIService


def test_post_ai_test_returns_model_response() -> None:
    """Verifica respuesta exitosa del endpoint de prueba AI."""
    mock_service = MagicMock(spec=AIService)
    mock_service.test_prompt.return_value = "¡Hola! ¿En qué puedo ayudarte?"

    app.dependency_overrides[get_ai_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post("/ai/test", json={"prompt": "Hola"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"response": "¡Hola! ¿En qué puedo ayudarte?"}
    mock_service.test_prompt.assert_called_once_with("Hola")


def test_post_ai_test_returns_503_on_ollama_error() -> None:
    """Verifica HTTP 503 cuando Ollama no está disponible."""
    mock_service = MagicMock(spec=AIService)
    mock_service.test_prompt.side_effect = OllamaConnectionError("No se pudo conectar con Ollama")

    app.dependency_overrides[get_ai_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post("/ai/test", json={"prompt": "Hola"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "No se pudo conectar" in response.json()["detail"]


def test_post_ai_test_validates_empty_prompt() -> None:
    """Verifica validación de prompt vacío."""
    with TestClient(app) as client:
        response = client.post("/ai/test", json={"prompt": ""})

    assert response.status_code == 422
