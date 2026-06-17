from app.domain.hybrid_context import HybridContext
from app.services.analytics_context_service import AnalyticsContextService
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService

class HybridContextService:

    def __init__(
        self,
        analytics_context_service: AnalyticsContextService,
        document_context_service: DocumentContextService,
        document_insights_service: DocumentInsightsService,
    ):
        self._analytics_context = analytics_context_service
        self._document_context = document_context_service
        self._document_insights = document_insights_service

    def build_context(self, question: str) -> HybridContext:
        snapshot = self._analytics_context.build_snapshot().to_dict()
        document_context = self._document_context.build_context(question)
        document_insights = self._document_insights.build_insights(document_context)
        return HybridContext(
            analytics_snapshot=snapshot,
            executive_insights=snapshot.get('executive_insights', {}),
            document_context=document_context.to_dict(),
            document_insights=document_insights.to_dict(),
        )
