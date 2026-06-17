from app.domain.hybrid_context import HybridContext
from app.services.hybrid_insights_service import HybridInsightsService

def _hybrid_context(
    dominant_customer: str | None = 'Farmacias de Similares',
    dominant_product: str | None = 'ARISTOCAPS-RB',
    risk_flags: list[str] | None = None,
    documents: list[dict[str, object]] | None = None,
    confidence_level: str = 'MEDIUM',
) -> HybridContext:
    risk_flags = risk_flags or ['Concentracion comercial moderada']
    documents = documents or [
        {
            'document_name': 'Manual_Clientes.pdf',
            'content': 'Procedimiento de registro de clientes comerciales',
            'score': 0.72,
        },
        {
            'document_name': 'ARISTOCAPS-RB_Manual.pdf',
            'content': 'Ficha del producto ARISTOCAPS-RB',
            'score': 0.68,
        },
    ]
    return HybridContext(
        analytics_snapshot={'summary': {'total_customers': 100}},
        executive_insights={
            'dominant_customer': dominant_customer,
            'dominant_product': dominant_product,
            'risk_flags': risk_flags,
        },
        document_context={
            'documents': documents,
            'sources': [str(item['document_name']) for item in documents],
            'top_document': str(documents[0]['document_name']),
            'total_matches': len(documents),
            'average_score': 0.7,
        },
        document_insights={
            'confidence_level': confidence_level,
            'source_documents': [str(item['document_name']) for item in documents],
            'total_matches': len(documents),
            'average_score': 0.7,
        },
    )

def test_build_insights_links_dominant_customer_with_documents() -> None:
    insights = HybridInsightsService().build_insights(
        '¿Qué cliente genera más ingresos y cuál es el procedimiento?',
        _hybrid_context(),
    )
    assert any('cliente dominante' in finding.lower() for finding in insights.cross_source_findings)
    assert 'Manual_Clientes.pdf' in insights.related_documents
    assert insights.confidence == 'MEDIUM'

def test_build_insights_links_dominant_product_with_manual() -> None:
    insights = HybridInsightsService().build_insights(
        '¿Cuál es nuestro producto principal y qué documentación existe?',
        _hybrid_context(),
    )
    assert any('producto dominante' in finding.lower() for finding in insights.cross_source_findings)
    assert 'ARISTOCAPS-RB_Manual.pdf' in insights.related_documents

def test_build_insights_links_risks_with_documents() -> None:
    insights = HybridInsightsService().build_insights(
        '¿Qué riesgos comerciales observas y qué documentos los respaldan?',
        _hybrid_context(),
    )
    assert any('riesgo comercial' in finding.lower() for finding in insights.cross_source_findings)

def test_build_insights_registration_question_finding() -> None:
    insights = HybridInsightsService().build_insights(
        '¿Cuántos clientes tenemos y cómo se registran?',
        _hybrid_context(dominant_customer=None, dominant_product=None, risk_flags=[]),
    )
    assert any('procedimientos documentados' in finding.lower() for finding in insights.cross_source_findings)
