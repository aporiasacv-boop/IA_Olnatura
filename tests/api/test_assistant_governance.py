from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.deps import get_business_assistant_service
from app.main import app
from app.services.business_assistant_service import BusinessAssistantService, GovernanceResult

def test_post_assistant_governance_success() -> None:
    mock_service = MagicMock(spec=BusinessAssistantService)
    mock_service.ask_governance.return_value = GovernanceResult(
        confidence='HIGH',
        evidence=['100 lineas de venta analizadas', 'Revenue total: 49722777.13 MXN'],
        answer='Farmacias de Similares concentra 42.2% de los ingresos observados.',
        source_type='analytics',
        source_tables=['venta_lineas', 'ventas', 'clientes'],
        source_documents=[],
        snapshot_date='2026-06-17',
        records_analyzed=100,
        generated_at='2026-06-17T16:00:00+00:00',
    )
    app.dependency_overrides[get_business_assistant_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/assistant/governance', json={'question': '¿Qué evidencia tienes?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['confidence'] == 'HIGH'
    assert data['source_type'] == 'analytics'
    assert 'venta_lineas' in data['source_tables']
    assert data['records_analyzed'] == 100
    assert data['evidence']
