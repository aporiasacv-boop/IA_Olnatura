from app.services.evidence_builder import EvidenceBuilder

_SNAPSHOT = {
    'summary': {'total_customers': 100, 'total_orders': 100},
    'financials': {'total_revenue': '49722777.13', 'total_lines': 100},
    'executive_insights': {
        'dominant_customer': 'FARMACIAS DE SIMILARES SA DE CV',
        'top_customer_share': 42.2,
        'dominant_product': 'ARISTOCAPS-RB',
        'top_product_share': 42.1,
    },
}

def test_build_analytics_evidence_includes_concentration() -> None:
    builder = EvidenceBuilder()
    evidence = builder.build_analytics_evidence(_SNAPSHOT)
    assert evidence
    assert 'SIMILARES' in evidence[0]['statement']
    assert any('100 lineas' in item for item in evidence[0]['evidence'])

def test_build_document_evidence_without_matches() -> None:
    builder = EvidenceBuilder()
    evidence = builder.build_document_evidence({'total_matches': 0}, {'average_score': 0.0, 'source_documents': []})
    assert 'fragmentos documentales' in evidence[0]['statement'].lower()

def test_flatten_evidence() -> None:
    builder = EvidenceBuilder()
    flattened = builder.flatten_evidence([
        {'statement': 'Cliente dominante identificado', 'evidence': ['100 lineas analizadas']},
    ])
    assert flattened == ['Cliente dominante identificado', '100 lineas analizadas']
