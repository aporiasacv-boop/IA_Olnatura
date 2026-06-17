import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import get_semantic_search_service
from app.db.schema import ensure_database_schema
from app.db.session import SessionLocal, engine
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService
from app.services.evidence_builder import EvidenceBuilder
from app.services.financial_analytics_service import FinancialAnalyticsService
from app.services.governance_service import GovernanceService

def main() -> int:
    print('=== VALIDACION ENTERPRISE GOVERNANCE ===')
    ensure_database_schema(engine)
    db = SessionLocal()
    try:
        analytics_context = AnalyticsContextService(
            AnalyticsService(AnalyticsRepository(db)),
            FinancialAnalyticsService(FinancialAnalyticsRepository(db)),
        )
        snapshot = analytics_context.build_snapshot().to_dict()
        governance = GovernanceService().build_analytics_governance(snapshot)
        print('governance_context:', json.dumps(governance.to_dict(), ensure_ascii=False, indent=2))
        semantic_search = get_semantic_search_service()
        document_context = DocumentContextService(semantic_search).build_context('procedimiento de ventas')
        document_insights = DocumentInsightsService().build_insights(document_context)
        document_governance = GovernanceService().build_document_governance(
            document_context.to_dict(),
            document_insights.to_dict(),
        )
        print('document_governance:', json.dumps(document_governance.to_dict(), ensure_ascii=False, indent=2))
        flattened = EvidenceBuilder().flatten_evidence(governance.evidence)
        print('evidence_flat:', json.dumps(flattened, ensure_ascii=False, indent=2))
        if governance.confidence_level != 'HIGH':
            print('ADVERTENCIA: confianza analitica no es HIGH', file=sys.stderr)
            return 1
        if not governance.evidence:
            print('ADVERTENCIA: sin evidencia analitica', file=sys.stderr)
            return 1
        if document_governance.source_type != 'documents':
            print('ADVERTENCIA: gobernanza documental invalida', file=sys.stderr)
            return 1
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
