import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import get_semantic_search_service
from app.db.session import SessionLocal, engine
from app.db.schema import ensure_database_schema
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService
from app.services.financial_analytics_service import FinancialAnalyticsService
from app.services.hybrid_context_service import HybridContextService
from app.services.hybrid_insights_service import HybridInsightsService

def main() -> int:
    print('=== VALIDACION INTELIGENCIA HIBRIDA ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        analytics_context = AnalyticsContextService(
            AnalyticsService(AnalyticsRepository(db)),
            FinancialAnalyticsService(FinancialAnalyticsRepository(db)),
        )
        semantic_search = get_semantic_search_service()
        hybrid_context_service = HybridContextService(
            analytics_context,
            DocumentContextService(semantic_search),
            DocumentInsightsService(),
        )
        hybrid_insights_service = HybridInsightsService()
        questions = [
            '¿Cuántos clientes tenemos y cómo se registran?',
            '¿Qué cliente genera más ingresos y qué documentación existe?',
        ]
        for question in questions:
            print(f'\n--- {question} ---')
            context = hybrid_context_service.build_context(question)
            insights = hybrid_insights_service.build_insights(question, context)
            print('hybrid_context:', json.dumps(context.to_dict(), ensure_ascii=False, indent=2)[:2500])
            print('hybrid_insights:', json.dumps(insights.to_dict(), ensure_ascii=False, indent=2))
            if not context.analytics_snapshot.get('summary'):
                print('ERROR: analytics_snapshot vacio', file=sys.stderr)
                return 1
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
