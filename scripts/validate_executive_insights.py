import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal, engine
from app.db.schema import ensure_database_schema
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService
from app.services.financial_analytics_service import FinancialAnalyticsService

def main() -> int:
    print('=== VALIDACION INTELIGENCIA EJECUTIVA ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        context = AnalyticsContextService(
            AnalyticsService(AnalyticsRepository(db)),
            FinancialAnalyticsService(FinancialAnalyticsRepository(db)),
        )
        snapshot = context.build_snapshot().to_dict()
        executive_insights = snapshot.get('executive_insights', {})
        financials = snapshot.get('financials', {})
        print('total_revenue:', financials.get('total_revenue'))
        print('executive_insights:', json.dumps(executive_insights, ensure_ascii=False, indent=2))
        if float(financials.get('total_revenue', '0')) <= 0:
            print('ADVERTENCIA: total_revenue no es mayor que cero', file=sys.stderr)
            return 1
        if not executive_insights:
            print('ERROR: executive_insights vacio', file=sys.stderr)
            return 1
        print('risk_flags_count:', len(executive_insights.get('risk_flags', [])))
        print('top_customer_share:', executive_insights.get('top_customer_share'))
        print('top_product_share:', executive_insights.get('top_product_share'))
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
