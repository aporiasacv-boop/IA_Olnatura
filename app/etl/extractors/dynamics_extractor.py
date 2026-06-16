import logging
from typing import Any
from app.etl.retry import with_retry
from app.integrations.dynamics.protocols import DynamicsClient

class DynamicsExtractor:

    def __init__(self, client: DynamicsClient, *, page_size: int=100, max_retries: int=3, retry_base_delay: float=1.0, logger: logging.Logger | None=None):
        self._client = client
        self._page_size = page_size
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay
        self._logger = logger or logging.getLogger(__name__)

    def extract_entity(self, entity_name: str, max_records: int | None=None) -> list[dict[str, Any]]:
        self._logger.info('Extrayendo entidad OData: %s', entity_name)
        records = with_retry(
            lambda: self._client.fetch_all_entity(entity_name, page_size=self._page_size),
            max_retries=self._max_retries,
            base_delay=self._retry_base_delay,
            logger=self._logger,
        )
        if max_records is not None:
            records = records[:max_records]
        self._logger.info('Extracción completada — %s: %s registros', entity_name, len(records))
        return records
