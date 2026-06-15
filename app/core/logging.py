"""
Configuración básica de logging para la aplicación.

Centraliza el formato y nivel de logs leyendo valores desde Settings.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """
    Configura el logging global de la aplicación.

    Se invoca una vez durante el arranque (lifespan startup).
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Reducir ruido de librerías externas en producción
    if not settings.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retorna un logger con el nombre del módulo solicitante."""
    return logging.getLogger(name)
