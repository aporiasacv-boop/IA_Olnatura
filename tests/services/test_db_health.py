"""
Pruebas del servicio DbHealthService.
"""

from unittest.mock import MagicMock, patch

from app.services.db_health import DbHealthService


def test_is_connected_returns_true_when_ping_succeeds() -> None:
    """Verifica conexión exitosa delegando en ping_database."""
    session = MagicMock()

    with patch("app.services.db_health.ping_database", return_value=True):
        service = DbHealthService(session)
        assert service.is_connected() is True


def test_is_connected_returns_false_when_ping_fails() -> None:
    """Verifica fallo de conexión cuando ping_database retorna False."""
    session = MagicMock()

    with patch("app.services.db_health.ping_database", return_value=False):
        service = DbHealthService(session)
        assert service.is_connected() is False
