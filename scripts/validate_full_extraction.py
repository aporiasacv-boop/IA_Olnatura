import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import create_dynamics_client
from app.core.config import settings
from app.db.schema import ensure_database_schema
from app.db.session import SessionLocal, engine
from app.etl.odata_filters import build_entity_filter
from app.etl.sync_dates import resolve_sync_date_range
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.venta_linea_repository import VentaLineaRepository
from app.repositories.venta_repository import VentaRepository
from app.services.sync_service import SyncService

def _d365_count(client, entity: str) -> int:
    start_date, end_date = resolve_sync_date_range(settings)
    odata_filter = build_entity_filter(entity, start_date, end_date)
    return client.count_entity(entity, odata_filter=odata_filter)

def main() -> int:
    print('=== VALIDACION EXTRACCION COMPLETA DYNAMICS ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    client = create_dynamics_client()
    try:
        expected_customers = _d365_count(client, settings.D365_CLIENTES_ENTITY)
        expected_sales = _d365_count(client, settings.D365_VENTAS_ENTITY)
        expected_lines = _d365_count(client, settings.D365_VENTAS_LINEAS_ENTITY)
        print(
            f'd365_esperado: clientes={expected_customers} '
            f'ventas={expected_sales} lineas={expected_lines}'
        )
        service = SyncService(db=db, dynamics_client=client)
        result = service.run()
        if result.errors:
            print(json.dumps({'errors': result.errors}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        customers_synced = ClienteRepository(db).count()
        sales_synced = VentaRepository(db).count()
        sales_lines_synced = VentaLineaRepository(db).count()
        matches_d365 = (
            customers_synced == expected_customers
            and sales_synced == expected_sales
            and sales_lines_synced == expected_lines
        )
        payload = {
            'customers_synced': customers_synced,
            'sales_synced': sales_synced,
            'sales_lines_synced': sales_lines_synced,
            'customers_d365': expected_customers,
            'sales_d365': expected_sales,
            'sales_lines_d365': expected_lines,
            'matches_d365': matches_d365,
            'duration_seconds': round(result.duration_seconds, 2),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if not matches_d365:
            print('ADVERTENCIA: totales PostgreSQL no coinciden con Dynamics', file=sys.stderr)
            return 1
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
