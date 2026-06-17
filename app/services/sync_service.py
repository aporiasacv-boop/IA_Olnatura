import logging
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from app.core.config import Settings, settings
from app.etl.extractors.dynamics_extractor import DynamicsExtractor
from app.etl.transformers.cliente_transformer import transform_clientes
from app.etl.transformers.venta_linea_transformer import transform_venta_lineas
from app.etl.transformers.venta_transformer import transform_ventas
from app.integrations.dynamics.exceptions import DynamicsError
from app.integrations.dynamics.protocols import DynamicsClient
from app.db.schema import ensure_database_schema
from app.models.venta import Venta
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.venta_linea_repository import VentaLineaRepository
from app.repositories.venta_repository import VentaRepository
from sqlalchemy import select

@dataclass
class EntitySyncResult:
    extracted: int = 0
    upserted: int = 0

@dataclass
class SyncResult:
    status: str = 'completed'
    clientes: EntitySyncResult = field(default_factory=EntitySyncResult)
    ventas: EntitySyncResult = field(default_factory=EntitySyncResult)
    errors: list[str] = field(default_factory=list)

@dataclass
class MvpSyncResult:
    entity: str
    read: int = 0
    inserted: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)

class SyncService:

    def __init__(self, db: Session, dynamics_client: DynamicsClient, app_settings: Settings | None=None, logger: logging.Logger | None=None):
        self._db = db
        self._dynamics_client = dynamics_client
        self._settings = app_settings or settings
        self._logger = logger or logging.getLogger(__name__)
        self._extractor = DynamicsExtractor(dynamics_client, page_size=self._settings.ETL_PAGE_SIZE, max_retries=self._settings.ETL_MAX_RETRIES, retry_base_delay=self._settings.ETL_RETRY_BASE_DELAY, logger=self._logger)
        self._cliente_repo = ClienteRepository(db)
        self._venta_repo = VentaRepository(db)
        self._venta_linea_repo = VentaLineaRepository(db)

    def run(self) -> SyncResult:
        self._logger.info('Iniciando sincronización ETL Dynamics → PostgreSQL')
        result = SyncResult()
        self._ensure_tables()
        result.clientes = self._sync_clientes(result.errors)
        result.ventas = self._sync_ventas(result.errors)
        if result.errors:
            result.status = 'completed_with_errors'
            self._logger.warning('Sincronización finalizada con errores: %s', result.errors)
        else:
            self._logger.info('Sincronización completada — clientes: %s, ventas: %s', result.clientes.upserted, result.ventas.upserted)
        return result

    def run_ventas(self) -> MvpSyncResult:
        self._logger.info('Iniciando sincronización ventas Dynamics → PostgreSQL')
        result = MvpSyncResult(entity=self._settings.D365_VENTAS_ENTITY_LABEL)
        self._ensure_tables()
        entity = self._settings.D365_VENTAS_ENTITY
        try:
            raw_records = self._extractor.extract_entity(entity, max_records=self._settings.SYNC_VENTAS_MAX_RECORDS)
            result.read = len(raw_records)
            transformed = transform_ventas(raw_records)
            self._logger.info('Transformadas %s ventas', len(transformed))
            inserted, updated = self._venta_repo.upsert_many_with_metrics(transformed)
            result.inserted = inserted
            result.updated = updated
            self._logger.info('Upsert ventas completado: %s insertados, %s actualizados', inserted, updated)
        except DynamicsError as exc:
            msg = f'Error sincronizando ventas: {exc.message}'
            self._logger.error(msg)
            result.errors.append(msg)
        except Exception as exc:
            msg = f'Error inesperado sincronizando ventas: {exc}'
            self._logger.exception(msg)
            result.errors.append(msg)
        return result

    def run_ventas_lineas(self) -> MvpSyncResult:
        self._logger.info('Iniciando sincronizacion lineas de venta Dynamics → PostgreSQL')
        result = MvpSyncResult(entity=self._settings.D365_VENTAS_LINEAS_ENTITY_LABEL)
        self._ensure_tables()
        entity = self._settings.D365_VENTAS_LINEAS_ENTITY
        try:
            raw_records = self._extractor.extract_entity(
                entity,
                max_records=self._settings.SYNC_VENTAS_LINEAS_MAX_RECORDS,
            )
            result.read = len(raw_records)
            transformed = transform_venta_lineas(raw_records)
            transformed = self._enrich_cliente_from_ventas(transformed)
            self._logger.info('Transformadas %s lineas de venta', len(transformed))
            inserted, updated = self._venta_linea_repo.upsert_many_with_metrics(transformed)
            result.inserted = inserted
            result.updated = updated
            self._logger.info(
                'Upsert lineas de venta completado: %s insertados, %s actualizados',
                inserted,
                updated,
            )
        except DynamicsError as exc:
            msg = f'Error sincronizando lineas de venta: {exc.message}'
            self._logger.error(msg)
            result.errors.append(msg)
        except Exception as exc:
            msg = f'Error inesperado sincronizando lineas de venta: {exc}'
            self._logger.exception(msg)
            result.errors.append(msg)
        return result

    def _enrich_cliente_from_ventas(self, records: list[dict]) -> list[dict]:
        missing_orders = {
            record['sales_order_number']
            for record in records
            if not record.get('cliente_dynamics_id')
        }
        if not missing_orders:
            return records
        mapping = {
            row.dynamics_id: row.cliente_dynamics_id
            for row in self._db.scalars(select(Venta).where(Venta.dynamics_id.in_(missing_orders)))
        }
        enriched: list[dict] = []
        for record in records:
            if record.get('cliente_dynamics_id'):
                enriched.append(record)
                continue
            cliente_id = mapping.get(record['sales_order_number'])
            enriched.append({**record, 'cliente_dynamics_id': cliente_id})
        return enriched

    def _ensure_tables(self) -> None:
        ensure_database_schema(self._db.get_bind())

    def _sync_clientes(self, errors: list[str]) -> EntitySyncResult:
        entity = self._settings.D365_CLIENTES_ENTITY
        sync_result = EntitySyncResult()
        try:
            raw_records = self._extractor.extract_entity(entity)
            sync_result.extracted = len(raw_records)
            transformed = transform_clientes(raw_records)
            self._logger.info('Transformados %s clientes', len(transformed))
            sync_result.upserted = self._cliente_repo.upsert_many(transformed)
            self._logger.info('Upsert clientes completado: %s registros', sync_result.upserted)
        except DynamicsError as exc:
            msg = f'Error sincronizando clientes: {exc.message}'
            self._logger.error(msg)
            errors.append(msg)
        except Exception as exc:
            msg = f'Error inesperado sincronizando clientes: {exc}'
            self._logger.exception(msg)
            errors.append(msg)
        return sync_result

    def _sync_ventas(self, errors: list[str]) -> EntitySyncResult:
        entity = self._settings.D365_VENTAS_ENTITY
        sync_result = EntitySyncResult()
        try:
            raw_records = self._extractor.extract_entity(entity)
            sync_result.extracted = len(raw_records)
            transformed = transform_ventas(raw_records)
            self._logger.info('Transformadas %s ventas', len(transformed))
            sync_result.upserted = self._venta_repo.upsert_many(transformed)
            self._logger.info('Upsert ventas completado: %s registros', sync_result.upserted)
        except DynamicsError as exc:
            msg = f'Error sincronizando ventas: {exc.message}'
            self._logger.error(msg)
            errors.append(msg)
        except Exception as exc:
            msg = f'Error inesperado sincronizando ventas: {exc}'
            self._logger.exception(msg)
            errors.append(msg)
        return sync_result
