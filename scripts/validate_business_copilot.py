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
from app.services.copilot_context_service import CopilotContextService
from app.services.copilot_insights_service import CopilotInsightsService
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService
from app.services.financial_analytics_service import FinancialAnalyticsService
from app.services.hybrid_context_service import HybridContextService
from app.services.hybrid_insights_service import HybridInsightsService

def main() -> int:
    print('=== VALIDACION BUSINESS COPILOT ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        analytics_context = AnalyticsContextService(
            AnalyticsService(AnalyticsRepository(db)),
            FinancialAnalyticsService(FinancialAnalyticsRepository(db)),
        )
        semantic_search = get_semantic_search_service()
        copilot_context_service = CopilotContextService(
            HybridContextService(
                analytics_context,
                DocumentContextService(semantic_search),
                DocumentInsightsService(),
            ),
            HybridInsightsService(),
            CopilotInsightsService(),
        )
        question = '¿Qué debería revisar?'
        context = copilot_context_service.build_context(question)
        print('copilot_insights:', json.dumps(context.copilot_insights, ensure_ascii=False, indent=2))
        if not context.copilot_insights.get('recommended_reviews'):
            print('ADVERTENCIA: sin revisiones sugeridas', file=sys.stderr)
        if not context.executive_insights.get('dominant_customer'):
            print('ADVERTENCIA: sin cliente dominante', file=sys.stderr)
            return 1
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
