"""
Servicio ETL de sincronización Dynamics 365 F&O → PostgreSQL.

Orquesta extracción OData, transformación y carga (upsert).
"""

import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.etl.extractors.dynamics_extractor import DynamicsExtractor
from app.etl.transformers.cliente_transformer import transform_clientes
from app.etl.transformers.venta_transformer import transform_ventas
from app.integrations.dynamics.exceptions import DynamicsError
from app.integrations.dynamics.protocols import DynamicsClient
from app.models.base import Base
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.venta_repository import VentaRepository


@dataclass
class EntitySyncResult:
    """Resultado de sincronización de una entidad."""

    extracted: int = 0
    upserted: int = 0


@dataclass
class SyncResult:
    """Resultado global del pipeline ETL."""

    status: str = "completed"
    clientes: EntitySyncResult = field(default_factory=EntitySyncResult)
    ventas: EntitySyncResult = field(default_factory=EntitySyncResult)
    errors: list[str] = field(default_factory=list)


class SyncService:
    """
    Pipeline ETL: Extract (OData) → Transform → Load (upsert PostgreSQL).

    Incluye logging estructurado y reintentos en la fase de extracción.
    """

    def __init__(
        self,
        db: Session,
        dynamics_client: DynamicsClient,
        app_settings: Settings | None = None,
        logger: logging.Logger | None = None,
    ):
        self._db = db
        self._dynamics_client = dynamics_client
        self._settings = app_settings or settings
        self._logger = logger or logging.getLogger(__name__)
        self._extractor = DynamicsExtractor(
            dynamics_client,
            page_size=self._settings.ETL_PAGE_SIZE,
            max_retries=self._settings.ETL_MAX_RETRIES,
            retry_base_delay=self._settings.ETL_RETRY_BASE_DELAY,
            logger=self._logger,
        )
        self._cliente_repo = ClienteRepository(db)
        self._venta_repo = VentaRepository(db)

    def run(self) -> SyncResult:
        """
        Ejecuta la sincronización completa de clientes y ventas.

        Returns:
            SyncResult con métricas y errores parciales si los hubo.
        """
        self._logger.info("Iniciando sincronización ETL Dynamics → PostgreSQL")
        result = SyncResult()

        self._ensure_tables()

        result.clientes = self._sync_clientes(result.errors)
        result.ventas = self._sync_ventas(result.errors)

        if result.errors:
            result.status = "completed_with_errors"
            self._logger.warning(
                "Sincronización finalizada con errores: %s", result.errors
            )
        else:
            self._logger.info(
                "Sincronización completada — clientes: %s, ventas: %s",
                result.clientes.upserted,
                result.ventas.upserted,
            )

        return result

    def _ensure_tables(self) -> None:
        """Crea tablas si no existen (desarrollo; usar Alembic en producción)."""
        Base.metadata.create_all(bind=self._db.get_bind())

    def _sync_clientes(self, errors: list[str]) -> EntitySyncResult:
        """Sincroniza la entidad de clientes."""
        entity = self._settings.D365_CLIENTES_ENTITY
        sync_result = EntitySyncResult()

        try:
            raw_records = self._extractor.extract_entity(entity)
            sync_result.extracted = len(raw_records)

            transformed = transform_clientes(raw_records)
            self._logger.info("Transformados %s clientes", len(transformed))

            sync_result.upserted = self._cliente_repo.upsert_many(transformed)
            self._logger.info("Upsert clientes completado: %s registros", sync_result.upserted)
        except DynamicsError as exc:
            msg = f"Error sincronizando clientes: {exc.message}"
            self._logger.error(msg)
            errors.append(msg)
        except Exception as exc:
            msg = f"Error inesperado sincronizando clientes: {exc}"
            self._logger.exception(msg)
            errors.append(msg)

        return sync_result

    def _sync_ventas(self, errors: list[str]) -> EntitySyncResult:
        """Sincroniza la entidad de ventas."""
        entity = self._settings.D365_VENTAS_ENTITY
        sync_result = EntitySyncResult()

        try:
            raw_records = self._extractor.extract_entity(entity)
            sync_result.extracted = len(raw_records)

            transformed = transform_ventas(raw_records)
            self._logger.info("Transformadas %s ventas", len(transformed))

            sync_result.upserted = self._venta_repo.upsert_many(transformed)
            self._logger.info("Upsert ventas completado: %s registros", sync_result.upserted)
        except DynamicsError as exc:
            msg = f"Error sincronizando ventas: {exc.message}"
            self._logger.error(msg)
            errors.append(msg)
        except Exception as exc:
            msg = f"Error inesperado sincronizando ventas: {exc}"
            self._logger.exception(msg)
            errors.append(msg)

        return sync_result
