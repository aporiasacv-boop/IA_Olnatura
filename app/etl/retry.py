"""
Utilidad de reintentos con backoff exponencial.
"""

import logging
import time
from collections.abc import Callable
from typing import TypeVar

from app.integrations.dynamics.exceptions import DynamicsError

T = TypeVar("T")


def with_retry(
    operation: Callable[[], T],
    *,
    max_retries: int = 3,
    base_delay: float = 1.0,
    logger: logging.Logger | None = None,
) -> T:
    """
    Ejecuta una operación con reintentos ante errores de Dynamics.

    Args:
        operation: Callable sin argumentos a ejecutar.
        max_retries: Número máximo de intentos.
        base_delay: Segundos base para backoff exponencial.
        logger: Logger opcional para registrar reintentos.

    Returns:
        Resultado de la operación exitosa.

    Raises:
        DynamicsError: Si todos los intentos fallan.
    """
    log = logger or logging.getLogger(__name__)
    last_error: DynamicsError | None = None

    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except DynamicsError as exc:
            last_error = exc
            if attempt == max_retries:
                log.error("Operación fallida tras %s intentos: %s", max_retries, exc.message)
                raise

            delay = base_delay * (2 ** (attempt - 1))
            log.warning(
                "Reintento %s/%s en %.1fs — %s",
                attempt,
                max_retries,
                delay,
                exc.message,
            )
            time.sleep(delay)

    raise last_error  # pragma: no cover
