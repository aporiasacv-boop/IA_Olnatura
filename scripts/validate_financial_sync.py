import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from app.db.session import SessionLocal, engine
from app.db.schema import ensure_database_schema
from app.integrations.dynamics.factory import create_dynamics_client
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService
from app.services.financial_analytics_service import FinancialAnalyticsService
from app.services.sync_service import SyncService

def main() -> int:
    print('=== VALIDACION FINANCIERA VENTA_LINEAS ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        dynamics_client = create_dynamics_client()
        sync = SyncService(db=db, dynamics_client=dynamics_client)
        result = sync.run_ventas_lineas()
        print('sync:', result)
        if result.errors:
            print('ERRORES SYNC:', result.errors, file=sys.stderr)
            return 1
        count = db.execute(text('SELECT COUNT(*) FROM venta_lineas')).scalar()
        total_revenue = db.execute(text('SELECT COALESCE(SUM(line_amount), 0) FROM venta_lineas')).scalar()
        print('COUNT venta_lineas =', count)
        print('SUM(line_amount) =', total_revenue)
        if count <= 0:
            return 1
        if float(total_revenue) <= 0:
            print('ADVERTENCIA: SUM(line_amount) no es mayor que cero', file=sys.stderr)
            return 1
        top_products = db.execute(text('''
            SELECT product_name, SUM(line_amount) AS revenue
            FROM venta_lineas
            GROUP BY product_name
            ORDER BY SUM(line_amount) DESC
            LIMIT 10
        ''')).all()
        print('TOP PRODUCTOS:', top_products)
        context = AnalyticsContextService(
            AnalyticsService(AnalyticsRepository(db)),
            FinancialAnalyticsService(FinancialAnalyticsRepository(db)),
        )
        snapshot = context.build_snapshot().to_dict()
        print('SNAPSHOT financials:', json.dumps(snapshot['financials'], ensure_ascii=False, indent=2))
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
