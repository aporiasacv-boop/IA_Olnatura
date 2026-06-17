from app.domain.document_context import DocumentContext
from app.services.document_insights_service import DocumentInsightsService

def test_build_insights_high_confidence() -> None:
    context = DocumentContext(
        documents=[],
        sources=['Manual.pdf'],
        top_document='Manual.pdf',
        total_matches=2,
        average_score=0.91,
        context='texto',
    )
    insights = DocumentInsightsService().build_insights(context)
    assert insights.confidence_level == 'HIGH'
    assert insights.top_document == 'Manual.pdf'
    assert insights.source_documents == ['Manual.pdf']

def test_build_insights_medium_confidence() -> None:
    context = DocumentContext(
        documents=[],
        sources=['Acta.pdf', 'Manual.pdf', 'Politica.pdf'],
        top_document='Acta.pdf',
        total_matches=3,
        average_score=0.72,
        context='texto',
    )
    insights = DocumentInsightsService().build_insights(context)
    assert insights.confidence_level == 'MEDIUM'
    assert len(insights.source_documents) == 3

def test_build_insights_low_confidence() -> None:
    context = DocumentContext(
        documents=[],
        sources=['Doc.pdf'],
        top_document='Doc.pdf',
        total_matches=1,
        average_score=0.45,
        context='texto',
    )
    insights = DocumentInsightsService().build_insights(context)
    assert insights.confidence_level == 'LOW'

def test_build_insights_empty_results_are_low() -> None:
    context = DocumentContext(
        documents=[],
        sources=[],
        top_document=None,
        total_matches=0,
        average_score=0.0,
        context='',
    )
    insights = DocumentInsightsService().build_insights(context)
    assert insights.confidence_level == 'LOW'
    assert insights.total_matches == 0
