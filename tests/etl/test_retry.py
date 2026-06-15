"""
Pruebas unitarias del mecanismo de reintentos ETL.
"""

from unittest.mock import MagicMock

import pytest

from app.etl.retry import with_retry
from app.integrations.dynamics.exceptions import DynamicsConnectionError


def test_with_retry_succeeds_on_first_attempt() -> None:
    """Verifica éxito sin reintentos."""
    operation = MagicMock(return_value="ok")
    result = with_retry(operation, max_retries=3, base_delay=0.01)
    assert result == "ok"
    assert operation.call_count == 1


def test_with_retry_succeeds_after_failures() -> None:
    """Verifica reintento exitoso tras fallos transitorios."""
    operation = MagicMock(
        side_effect=[
            DynamicsConnectionError("timeout"),
            DynamicsConnectionError("timeout"),
            "ok",
        ]
    )
    result = with_retry(operation, max_retries=3, base_delay=0.01)
    assert result == "ok"
    assert operation.call_count == 3


def test_with_retry_raises_after_max_attempts() -> None:
    """Verifica que se agotan los reintentos y se propaga el error."""
    operation = MagicMock(
        side_effect=DynamicsConnectionError("timeout"),
    )
    with pytest.raises(DynamicsConnectionError):
        with_retry(operation, max_retries=2, base_delay=0.01)
    assert operation.call_count == 2
