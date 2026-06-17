import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db.schema import ensure_database_schema
from app.db.session import SessionLocal, engine
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository
from app.repositories.organizational_snapshot_repository import OrganizationalSnapshotRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService
from app.services.financial_analytics_service import FinancialAnalyticsService
from app.services.memory_insights_service import MemoryInsightsService
from app.services.snapshot_memory_service import SnapshotMemoryService


def main() -> int:
    print('=== VALIDACION MEMORIA EMPRESARIAL ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        analytics_context = AnalyticsContextService(
            AnalyticsService(AnalyticsRepository(db)),
            FinancialAnalyticsService(FinancialAnalyticsRepository(db)),
        )
        service = SnapshotMemoryService(
            OrganizationalSnapshotRepository(db),
            analytics_context,
            MemoryInsightsService(),
        )
        saved = service.save_snapshot()
        print('snapshot_guardado:', json.dumps(saved, ensure_ascii=False, indent=2))
        comparison = service.compare_snapshots()
        print('comparacion:', json.dumps(comparison, ensure_ascii=False, indent=2))
        if saved['total_customers'] <= 0:
            print('ADVERTENCIA: total_customers invalido', file=sys.stderr)
            return 1
        if not saved.get('top_customer'):
            print('ADVERTENCIA: sin cliente dominante', file=sys.stderr)
            return 1
        insights = comparison['memory_insights']
        if not insights.get('stable_findings') and not insights.get('changes'):
            print('ADVERTENCIA: sin hallazgos de memoria', file=sys.stderr)
            return 1
        return 0
    finally:
        db.close()


if __name__ == '__main__':
    raise SystemExit(main())
