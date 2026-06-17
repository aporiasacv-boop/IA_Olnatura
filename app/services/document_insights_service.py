from app.domain.document_context import DocumentContext
from app.domain.document_insights import DocumentInsights

class DocumentInsightsService:

    def build_insights(self, document_context: DocumentContext) -> DocumentInsights:
        confidence_level = self._confidence_level(document_context.average_score, document_context.total_matches)
        return DocumentInsights(
            total_matches=document_context.total_matches,
            confidence_level=confidence_level,
            top_document=document_context.top_document,
            source_documents=list(document_context.sources),
            average_score=document_context.average_score,
        )

    @staticmethod
    def _confidence_level(average_score: float, total_matches: int) -> str:
        if total_matches == 0:
            return 'LOW'
        if average_score > 0.80:
            return 'HIGH'
        if average_score >= 0.60:
            return 'MEDIUM'
        return 'LOW'
