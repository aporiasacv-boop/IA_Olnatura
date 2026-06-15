"""
Pruebas del servicio DynamicsHealthService.
"""

from unittest.mock import MagicMock

from app.integrations.dynamics.exceptions import DynamicsODataError
from app.services.dynamics_health import DynamicsHealthService


def test_is_connected_returns_true_when_ping_succeeds() -> None:
    """Verifica conexión exitosa cuando ping no lanza excepción."""
    client = MagicMock()
    client.ping.return_value = None

    service = DynamicsHealthService(client)

    assert service.is_connected() is True
    client.ping.assert_called_once()


def test_is_connected_returns_false_when_ping_fails() -> None:
    """Verifica fallo de conexión cuando ping lanza DynamicsError."""
    client = MagicMock()
    client.ping.side_effect = DynamicsODataError("Error OData 503", status_code=503)

    service = DynamicsHealthService(client)

    assert service.is_connected() is False
