import logging
from app.core.logging import get_logger, setup_logging

def test_setup_logging_configures_root_logger() -> None:
    setup_logging()
    assert logging.getLogger().level == logging.INFO

def test_get_logger_returns_named_logger() -> None:
    logger = get_logger('test.module')
    assert logger.name == 'test.module'
