from unittest.mock import MagicMock

from app.domain.document_context import DocumentContext
from app.domain.document_insights import DocumentInsights
from app.services.analytics_context_service import AnalyticsContextService
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService
from app.services.hybrid_context_service import HybridContextService

def test_build_context_consolidates_analytics_and_documents() -> None:
    analytics_context = MagicMock(spec=AnalyticsContextService)
    snapshot = MagicMock()
    snapshot.to_dict.return_value = {
        'summary': {'total_customers': 100},
        'financials': {'total_revenue': '1000.00'},
        'executive_insights': {'dominant_customer': 'Alpha'},
    }
    analytics_context.build_snapshot.return_value = snapshot
    document_context = MagicMock(spec=DocumentContextService)
    document_context.build_context.return_value = DocumentContext(
        documents=[{'document_name': 'Manual_Clientes.pdf', 'score': 0.9, 'content': 'Registro de clientes'}],
        sources=['Manual_Clientes.pdf'],
        top_document='Manual_Clientes.pdf',
        total_matches=1,
        average_score=0.9,
        context='texto',
    )
    document_insights = MagicMock(spec=DocumentInsightsService)
    document_insights.build_insights.return_value = DocumentInsights(
        total_matches=1,
        confidence_level='HIGH',
        top_document='Manual_Clientes.pdf',
        source_documents=['Manual_Clientes.pdf'],
        average_score=0.9,
    )
    service = HybridContextService(analytics_context, document_context, document_insights)
    context = service.build_context('¿Cuántos clientes tenemos y cómo se registran?')
    payload = context.to_dict()
    assert payload['analytics_snapshot']['summary']['total_customers'] == 100
    assert payload['executive_insights']['dominant_customer'] == 'Alpha'
    assert payload['document_context']['top_document'] == 'Manual_Clientes.pdf'
    assert payload['document_insights']['confidence_level'] == 'HIGH'
