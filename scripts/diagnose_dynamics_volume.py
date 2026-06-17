import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import create_dynamics_client
from app.db.schema import ensure_database_schema
from app.db.session import SessionLocal, engine
from app.services.volume_diagnostics_service import VolumeDiagnosticsService, explain_hundred_records

def main() -> int:
    print('=== DIAGNOSTICO DE VOLUMEN DYNAMICS VS POSTGRESQL ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        service = VolumeDiagnosticsService(db=db, dynamics_client=create_dynamics_client())
        report = service.run()
        payload = report.to_report_dict()
        payload['explanation'] = explain_hundred_records(report)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if not report.pagination_working:
            print('ADVERTENCIA: paginacion incompleta o truncada', file=sys.stderr)
            return 1
        if not report.filters_working:
            print('ADVERTENCIA: filtros OData invalidos', file=sys.stderr)
            return 1
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
