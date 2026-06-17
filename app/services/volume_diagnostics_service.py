import inspect
import os
import time
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.domain.volume_diagnostics import EntityVolumeDiagnostics, VolumeDiagnosticsReport
from app.etl.extractors.dynamics_extractor import DynamicsExtractor
from app.etl.odata_filters import build_entity_filter
from app.etl.sync_dates import resolve_sync_date_range
from app.integrations.dynamics.exceptions import DynamicsODataError
from app.integrations.dynamics.odata_client import DynamicsODataClient
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.venta_linea_repository import VentaLineaRepository
from app.repositories.venta_repository import VentaRepository
from app.services.sync_service import SyncService

_LEGACY_LIMIT_ENV_VARS = (
    'SYNC_CLIENTES_MAX_RECORDS',
    'SYNC_VENTAS_MAX_RECORDS',
    'SYNC_VENTAS_LINEAS_MAX_RECORDS',
)

class VolumeDiagnosticsService:

    def __init__(
        self,
        db: Session,
        dynamics_client: DynamicsODataClient,
        app_settings: Settings | None = None,
    ):
        self._db = db
        self._client = dynamics_client
        self._settings = app_settings or settings

    def run(self) -> VolumeDiagnosticsReport:
        started_at = time.perf_counter()
        start_date, end_date = resolve_sync_date_range(self._settings)
        artificial_notes = self._detect_artificial_limits()
        entities: dict[str, EntityVolumeDiagnostics] = {}
        entities[self._settings.D365_CLIENTES_ENTITY] = self._diagnose_entity(
            self._settings.D365_CLIENTES_ENTITY,
            start_date,
            end_date,
        )
        entities[self._settings.D365_VENTAS_ENTITY] = self._diagnose_entity(
            self._settings.D365_VENTAS_ENTITY,
            start_date,
            end_date,
        )
        entities[self._settings.D365_VENTAS_LINEAS_ENTITY] = self._diagnose_entity(
            self._settings.D365_VENTAS_LINEAS_ENTITY,
            start_date,
            end_date,
        )
        customers = entities[self._settings.D365_CLIENTES_ENTITY]
        sales = entities[self._settings.D365_VENTAS_ENTITY]
        lines = entities[self._settings.D365_VENTAS_LINEAS_ENTITY]
        pagination_working = all(
            not diag.possible_page_size_truncation and diag.count_matches_pagination is not False
            for diag in entities.values()
        )
        filters_working = all(diag.filter_valid for diag in entities.values())
        return VolumeDiagnosticsReport(
            customers_d365=customers.total_records,
            customers_postgres=ClienteRepository(self._db).count(),
            sales_d365=sales.total_records,
            sales_postgres=VentaRepository(self._db).count(),
            sales_lines_d365=lines.total_records,
            sales_lines_postgres=VentaLineaRepository(self._db).count(),
            pagination_working=pagination_working,
            filters_working=filters_working,
            duration_seconds=time.perf_counter() - started_at,
            sync_start_date=start_date.isoformat() if start_date else None,
            sync_end_date=end_date.isoformat() if end_date else None,
            artificial_limits_detected=bool(artificial_notes),
            artificial_limit_notes=tuple(artificial_notes),
            entities=entities,
        )

    def _diagnose_entity(
        self,
        entity_name: str,
        start_date: object,
        end_date: object,
    ) -> EntityVolumeDiagnostics:
        odata_filter = build_entity_filter(entity_name, start_date, end_date)
        filter_valid, filter_error = self._client.validate_filter(entity_name, odata_filter)
        odata_count: int | None = None
        if filter_valid:
            try:
                odata_count = self._client.count_entity(entity_name, odata_filter=odata_filter)
            except DynamicsODataError:
                odata_count = None
        pagination = self._client.paginate_entity_stats(
            entity_name,
            page_size=self._settings.ETL_PAGE_SIZE,
            odata_filter=odata_filter if filter_valid else None,
        )
        count_matches_pagination: bool | None
        if odata_count is None:
            count_matches_pagination = None
        else:
            count_matches_pagination = odata_count == pagination.total_records
        possible_truncation = self._detect_possible_truncation(
            pagination.total_records,
            pagination.pages_traversed,
            pagination.records_per_page,
            odata_count,
            self._settings.ETL_PAGE_SIZE,
        )
        return EntityVolumeDiagnostics(
            entity_name=entity_name,
            total_records=pagination.total_records,
            odata_count=odata_count,
            pages_traversed=pagination.pages_traversed,
            next_links_found=pagination.next_links_found,
            records_per_page=pagination.records_per_page,
            odata_filter=odata_filter,
            filter_valid=filter_valid,
            filter_error=filter_error,
            duration_seconds=pagination.duration_seconds,
            count_matches_pagination=count_matches_pagination,
            possible_page_size_truncation=possible_truncation,
        )

    @staticmethod
    def _detect_possible_truncation(
        total_records: int,
        pages_traversed: int,
        records_per_page: tuple[int, ...],
        odata_count: int | None,
        page_size: int,
    ) -> bool:
        if odata_count is not None and total_records != odata_count:
            return True
        if not records_per_page:
            return False
        last_page_full = records_per_page[-1] == page_size
        if pages_traversed == 1 and last_page_full and total_records == page_size:
            return odata_count is None
        return False

    def _detect_artificial_limits(self) -> list[str]:
        notes: list[str] = []
        for env_var in _LEGACY_LIMIT_ENV_VARS:
            if os.environ.get(env_var):
                notes.append(
                    f'{env_var}={os.environ[env_var]} presente en entorno; la aplicacion ya no lo aplica'
                )
        if hasattr(self._settings, 'SYNC_VENTAS_MAX_RECORDS'):
            notes.append('SYNC_*_MAX_RECORDS aun definido en Settings')
        extractor_source = inspect.getsource(DynamicsExtractor.extract_entity)
        if 'max_records' in extractor_source:
            notes.append('DynamicsExtractor.extract_entity aun referencia max_records')
        sync_source = inspect.getsource(SyncService.run_ventas)
        if 'max_records' in sync_source or 'SYNC_VENTAS_MAX_RECORDS' in sync_source:
            notes.append('SyncService.run_ventas aun referencia limites artificiales')
        return notes

def explain_hundred_records(report: VolumeDiagnosticsReport) -> str:
    reasons: list[str] = []
    if report.artificial_limits_detected:
        reasons.append(
            'Existen variables legacy SYNC_*_MAX_RECORDS en el entorno; '
            'fueron usadas por el MVP para truncar a 100 registros.'
        )
    if not report.sync_start_date or not report.sync_end_date:
        reasons.append(
            'SYNC_START_DATE y SYNC_END_DATE no estan configurados; '
            'ventas y lineas se consultan sin filtro de rango.'
        )
    reasons.append(
        f'ETL_PAGE_SIZE={settings.ETL_PAGE_SIZE} define el tamano de pagina OData, no un tope total.'
    )
    for entity_name, diag in report.entities.items():
        if diag.total_records == settings.ETL_PAGE_SIZE and diag.pages_traversed == 1:
            if diag.odata_count is not None and diag.odata_count > diag.total_records:
                reasons.append(
                    f'{entity_name}: Dynamics reporta {diag.odata_count} registros via $count, '
                    f'pero la paginacion solo obtuvo {diag.total_records}; '
                    'la paginacion no recorrio todas las paginas.'
                )
            elif diag.odata_count == diag.total_records:
                reasons.append(
                    f'{entity_name}: Dynamics contiene exactamente {diag.total_records} registros '
                    f'({"con filtro aplicado" if diag.odata_filter else "sin filtro"}); '
                    'PostgreSQL refleja el volumen real disponible en OData.'
                )
            else:
                reasons.append(
                    f'{entity_name}: se obtuvo una sola pagina de {diag.total_records} registros '
                    f'sin @odata.nextLink; si existen mas registros en D365, la paginacion no avanzo.'
                )
        if diag.possible_page_size_truncation:
            reasons.append(
                f'{entity_name}: posible truncamiento en pagina ({diag.total_records} leidos, '
                f'$count={diag.odata_count}).'
            )
        if report.customers_postgres == report.customers_d365 == 100:
            pass
    if (
        report.customers_postgres == report.sales_postgres == report.sales_lines_postgres == 100
        and all(diag.pages_traversed == 1 for diag in report.entities.values())
    ):
        reasons.append(
            'Los tres totales coinciden en 100 porque el historico MVP sincronizo exactamente '
            '100 filas por entidad y el espejo PostgreSQL conserva ese volumen hasta una sync completa.'
        )
    return ' '.join(dict.fromkeys(reasons))
