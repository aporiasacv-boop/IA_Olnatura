from unittest.mock import MagicMock, patch
from app.services.db_health import DbHealthService

def test_is_connected_returns_true_when_ping_succeeds() -> None:
    session = MagicMock()
    with patch('app.services.db_health.ping_database', return_value=True):
        service = DbHealthService(session)
        assert service.is_connected() is True

def test_is_connected_returns_false_when_ping_fails() -> None:
    session = MagicMock()
    with patch('app.services.db_health.ping_database', return_value=False):
        service = DbHealthService(session)
        assert service.is_connected() is False
