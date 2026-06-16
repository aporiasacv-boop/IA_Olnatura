from collections.abc import Generator
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.api.deps import get_natural_chat_service
from app.integrations.ollama.exceptions import OllamaConnectionError
from app.main import app
from app.services.natural_chat_service import NaturalChatResult, NaturalChatService

@pytest.fixture
def natural_chat_client(analytics_db: Session) -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client

def test_post_chat_natural_with_mocked_service() -> None:
    mock_service = MagicMock(spec=NaturalChatService)
    mock_service.process.return_value = NaturalChatResult(
        question='¿Cuántos clientes tenemos?',
        intent='customers_count',
        answer='Actualmente existen 100 clientes sincronizados desde Dynamics 365 Finance & Operations.',
    )
    app.dependency_overrides[get_natural_chat_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/chat/natural', json={'question': '¿Cuántos clientes tenemos?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['intent'] == 'customers_count'
    assert '100 clientes' in data['answer']
    mock_service.process.assert_called_once_with('¿Cuántos clientes tenemos?')

def test_post_chat_natural_returns_503_on_ollama_error() -> None:
    mock_service = MagicMock(spec=NaturalChatService)
    mock_service.process.side_effect = OllamaConnectionError('No se pudo conectar con Ollama')
    app.dependency_overrides[get_natural_chat_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/chat/natural', json={'question': '¿Cuántos clientes tenemos?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503

def test_post_chat_natural_validates_empty_question() -> None:
    with TestClient(app) as client:
        response = client.post('/chat/natural', json={'question': ''})
    assert response.status_code == 422

def test_post_chat_natural_unknown_intent(natural_chat_client: TestClient) -> None:
    mock_service = MagicMock(spec=NaturalChatService)
    mock_service.process.return_value = NaturalChatResult(
        question='¿Qué es un ERP?',
        intent='unknown',
        answer='No dispongo de datos empresariales para responder esa pregunta en el sistema actual.',
    )
    app.dependency_overrides[get_natural_chat_service] = lambda: mock_service
    try:
        response = natural_chat_client.post('/chat/natural', json={'question': '¿Qué es un ERP?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()['intent'] == 'unknown'
