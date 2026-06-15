"""
Pruebas del endpoint GET /dynamics/health.
"""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.integrations.dynamics.factory import create_dynamics_client
from app.integrations.dynamics.exceptions import DynamicsODataError
from app.main import app


def test_dynamics_health_returns_connected() -> None:
    """Verifica respuesta exitosa cuando Dynamics responde correctamente."""
    mock_client = MagicMock()
    mock_client.ping.return_value = None

    app.dependency_overrides[create_dynamics_client] = lambda: mock_client
    try:
        with TestClient(app) as client:
            response = client.get("/dynamics/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"dynamics": "connected"}


def test_dynamics_health_returns_503_when_unavailable() -> None:
    """Verifica HTTP 503 cuando Dynamics no responde."""
    mock_client = MagicMock()
    mock_client.ping.side_effect = DynamicsODataError("Error OData 503", status_code=503)

    app.dependency_overrides[create_dynamics_client] = lambda: mock_client
    try:
        with TestClient(app) as client:
            response = client.get("/dynamics/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"] == "Dynamics unavailable"
