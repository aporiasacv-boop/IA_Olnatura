from app.domain.copilot_context import CopilotContext
from app.services.copilot_insights_service import CopilotInsightsService
from app.services.hybrid_context_service import HybridContextService
from app.services.hybrid_insights_service import HybridInsightsService

class CopilotContextService:

    def __init__(
        self,
        hybrid_context_service: HybridContextService,
        hybrid_insights_service: HybridInsightsService,
        copilot_insights_service: CopilotInsightsService,
    ):
        self._hybrid_context = hybrid_context_service
        self._hybrid_insights = hybrid_insights_service
        self._copilot_insights = copilot_insights_service

    def build_context(self, question: str) -> CopilotContext:
        hybrid_context = self._hybrid_context.build_context(question)
        hybrid_insights = self._hybrid_insights.build_insights(question, hybrid_context)
        hybrid_payload = hybrid_insights.to_dict()
        hybrid_payload['document_confidence_level'] = hybrid_context.document_insights.get('confidence_level')
        copilot_insights = self._copilot_insights.build_insights(
            analytics_snapshot=hybrid_context.analytics_snapshot,
            executive_insights=hybrid_context.executive_insights,
            hybrid_insights=hybrid_payload,
        )
        return CopilotContext(
            analytics_snapshot=hybrid_context.analytics_snapshot,
            executive_insights=hybrid_context.executive_insights,
            hybrid_insights=hybrid_payload,
            copilot_insights=copilot_insights.to_dict(),
        )
