import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import create_dynamics_client
from app.core.config import settings
from app.db.schema import ensure_database_schema
from app.db.session import SessionLocal, engine
from app.etl.sync_dates import resolve_sync_date_range
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.venta_linea_repository import VentaLineaRepository
from app.repositories.venta_repository import VentaRepository
from app.services.sync_service import SyncService

def main() -> int:
    print('=== VALIDACION SYNC ANUAL COMPLETO ===')
    start_date, end_date = resolve_sync_date_range(settings)
    print(f'rango_configurado: {start_date} -> {end_date}')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        service = SyncService(db=db, dynamics_client=create_dynamics_client())
        result = service.run()
        cliente_count = ClienteRepository(db).count()
        venta_count = VentaRepository(db).count()
        venta_linea_count = VentaLineaRepository(db).count()
        payload = {
            'status': result.status,
            'duration_seconds': round(result.duration_seconds, 2),
            'clientes': {
                'read': result.clientes.extracted,
                'inserted': result.clientes.inserted,
                'updated': result.clientes.updated,
                'postgres_total': cliente_count,
            },
            'ventas': {
                'read': result.ventas.extracted,
                'inserted': result.ventas.inserted,
                'updated': result.ventas.updated,
                'postgres_total': venta_count,
            },
            'venta_lineas': {
                'read': result.venta_lineas.extracted,
                'inserted': result.venta_lineas.inserted,
                'updated': result.venta_lineas.updated,
                'postgres_total': venta_linea_count,
            },
            'errors': result.errors,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if result.errors:
            print('ADVERTENCIA: sincronizacion con errores', file=sys.stderr)
            return 1
        if cliente_count <= 0:
            print('ADVERTENCIA: sin clientes en PostgreSQL', file=sys.stderr)
            return 1
        if venta_count <= 0:
            print('ADVERTENCIA: sin ventas en PostgreSQL', file=sys.stderr)
            return 1
        if venta_linea_count <= 0:
            print('ADVERTENCIA: sin venta_lineas en PostgreSQL', file=sys.stderr)
            return 1
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
