import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService

def main() -> int:
    db = SessionLocal()
    try:
        service = AnalyticsContextService(AnalyticsService(AnalyticsRepository(db)))
        snapshot = service.build_snapshot().to_dict()
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        if snapshot['summary']['total_customers'] <= 0:
            print('ADVERTENCIA: no hay clientes en PostgreSQL', file=sys.stderr)
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
