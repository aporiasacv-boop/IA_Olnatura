"""
Pruebas del módulo de logging.
"""

import logging

from app.core.logging import get_logger, setup_logging


def test_setup_logging_configures_root_logger() -> None:
    """Verifica que setup_logging establece el nivel del logger raíz."""
    setup_logging()
    assert logging.getLogger().level == logging.INFO


def test_get_logger_returns_named_logger() -> None:
    """Verifica que get_logger retorna un logger con el nombre indicado."""
    logger = get_logger("test.module")
    assert logger.name == "test.module"
