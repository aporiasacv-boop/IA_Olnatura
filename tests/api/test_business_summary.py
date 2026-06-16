from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.api.deps import get_business_interpretation_service
from app.integrations.ollama.exceptions import OllamaConnectionError
from app.main import app
from app.services.business_interpretation_service import BusinessInterpretationService

def test_post_business_summary_returns_interpretation() -> None:
    mock_service = MagicMock(spec=BusinessInterpretationService)
    mock_service.generate_summary.return_value = 'Las ventas del mes reflejan un volumen significativo con una base de clientes activa.'
    app.dependency_overrides[get_business_interpretation_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/ai/business-summary', json={'ventas_mes': 125000, 'clientes': 230})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert 'summary' in data
    assert 'ventas' in data['summary'].lower() or 'clientes' in data['summary'].lower()
    mock_service.generate_summary.assert_called_once_with(ventas_mes=125000, clientes=230)

def test_post_business_summary_returns_503_on_ollama_error() -> None:
    mock_service = MagicMock(spec=BusinessInterpretationService)
    mock_service.generate_summary.side_effect = OllamaConnectionError('No se pudo conectar con Ollama')
    app.dependency_overrides[get_business_interpretation_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/ai/business-summary', json={'ventas_mes': 125000, 'clientes': 230})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert 'No se pudo conectar' in response.json()['detail']

def test_post_business_summary_validates_negative_values() -> None:
    with TestClient(app) as client:
        response = client.post('/ai/business-summary', json={'ventas_mes': -1, 'clientes': 230})
    assert response.status_code == 422
