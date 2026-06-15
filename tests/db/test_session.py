"""
Pruebas de conexión y ping de PostgreSQL.
"""

from unittest.mock import MagicMock

from app.db.session import ping_database


def test_ping_database_returns_true_when_select_1_succeeds() -> None:
    """Verifica que SELECT 1 exitoso retorna True."""
    session = MagicMock()
    session.execute.return_value.scalar.return_value = 1

    assert ping_database(session) is True


def test_ping_database_returns_false_when_result_is_not_1() -> None:
    """Verifica que un resultado distinto de 1 se considera fallo."""
    session = MagicMock()
    session.execute.return_value.scalar.return_value = 0

    assert ping_database(session) is False
