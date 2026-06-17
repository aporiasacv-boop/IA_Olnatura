import logging
from typing import Any

from app.etl.odata_filters import build_entity_filter
from app.etl.retry import with_retry
from app.etl.sync_dates import resolve_sync_date_range
from app.core.config import Settings, settings
from app.integrations.dynamics.protocols import DynamicsClient

class DynamicsExtractor:

    def __init__(
        self,
        client: DynamicsClient,
        *,
        page_size: int = 100,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        app_settings: Settings | None = None,
        logger: logging.Logger | None = None,
    ):
        self._client = client
        self._page_size = page_size
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay
        self._settings = app_settings or settings
        self._logger = logger or logging.getLogger(__name__)

    def extract_entity(self, entity_name: str) -> list[dict[str, Any]]:
        start_date, end_date = resolve_sync_date_range(self._settings)
        odata_filter = build_entity_filter(entity_name, start_date, end_date)
        if odata_filter:
            self._logger.info(
                'Extrayendo entidad OData: %s con filtro de fechas %s a %s',
                entity_name,
                start_date,
                end_date,
            )
        else:
            self._logger.info('Extrayendo entidad OData: %s sin filtro de fechas', entity_name)
        records = with_retry(
            lambda: self._client.fetch_all_entity(
                entity_name,
                page_size=self._page_size,
                odata_filter=odata_filter,
            ),
            max_retries=self._max_retries,
            base_delay=self._retry_base_delay,
            logger=self._logger,
        )
        self._logger.info('Extraccion completada — %s: %s registros', entity_name, len(records))
        return records
