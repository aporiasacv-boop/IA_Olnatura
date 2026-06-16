from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.api.deps import get_business_assistant_service
from app.integrations.ollama.exceptions import OllamaConnectionError
from app.main import app
from app.services.business_assistant_service import AssistantResult, BusinessAssistantService

def test_post_assistant_analytics_response() -> None:
    mock_service = MagicMock(spec=BusinessAssistantService)
    mock_service.ask.return_value = AssistantResult(
        source='analytics',
        answer='Actualmente existen 100 clientes sincronizados desde Dynamics 365 Finance & Operations.',
    )
    app.dependency_overrides[get_business_assistant_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/assistant', json={'question': '¿Cuántos clientes tenemos?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'analytics'
    assert '100 clientes' in data['answer']
    mock_service.ask.assert_called_once_with('¿Cuántos clientes tenemos?')

def test_post_assistant_documents_response() -> None:
    mock_service = MagicMock(spec=BusinessAssistantService)
    mock_service.ask.return_value = AssistantResult(
        source='documents',
        answer='El objeto social de la empresa es comercializar productos naturales.',
    )
    app.dependency_overrides[get_business_assistant_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/assistant', json={'question': '¿Cuál es el objeto social de la empresa?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'documents'
    assert 'objeto social' in data['answer'].lower()

def test_post_assistant_returns_503_on_ollama_error() -> None:
    mock_service = MagicMock(spec=BusinessAssistantService)
    mock_service.ask.side_effect = OllamaConnectionError('No se pudo conectar con Ollama')
    app.dependency_overrides[get_business_assistant_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/assistant', json={'question': '¿Cuál es el objeto social?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503

def test_post_assistant_validates_empty_question() -> None:
    with TestClient(app) as client:
        response = client.post('/assistant', json={'question': ''})
    assert response.status_code == 422

def test_post_assistant_hybrid_response() -> None:
    mock_service = MagicMock(spec=BusinessAssistantService)
    mock_service.ask.return_value = AssistantResult(
        source='hybrid',
        answer='Hay 100 clientes y se registran mediante el modulo de ventas en Dynamics.',
    )
    app.dependency_overrides[get_business_assistant_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post(
                '/assistant',
                json={'question': '¿Cuántos clientes tenemos y cómo se registran?'},
            )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'hybrid'
    assert '100 clientes' in data['answer']
