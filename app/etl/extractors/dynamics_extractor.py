"""
Extractor OData para Dynamics 365 F&O.

Responsable de la fase Extract del pipeline ETL.
"""

import logging
from typing import Any

from app.etl.retry import with_retry
from app.integrations.dynamics.protocols import DynamicsClient


class DynamicsExtractor:
    """Extrae registros de entidades OData con reintentos y paginación."""

    def __init__(
        self,
        client: DynamicsClient,
        *,
        page_size: int = 100,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        logger: logging.Logger | None = None,
    ):
        self._client = client
        self._page_size = page_size
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay
        self._logger = logger or logging.getLogger(__name__)

    def extract_entity(self, entity_name: str) -> list[dict[str, Any]]:
        """
        Extrae todos los registros de una entidad OData.

        Args:
            entity_name: Nombre de la entidad en Dynamics 365 F&O.

        Returns:
            Lista de registros crudos de OData.
        """
        self._logger.info("Extrayendo entidad OData: %s", entity_name)

        records = with_retry(
            lambda: self._client.fetch_all_entity(entity_name, page_size=self._page_size),
            max_retries=self._max_retries,
            base_delay=self._retry_base_delay,
            logger=self._logger,
        )

        self._logger.info(
            "Extracción completada — %s: %s registros",
            entity_name,
            len(records),
        )
        return records
