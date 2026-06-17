from app.services.governance_service import GovernanceService

_SNAPSHOT = {
    'summary': {'total_customers': 100, 'total_orders': 100},
    'financials': {'total_revenue': '49722777.13', 'total_lines': 100},
    'date_range': {'start_date': '2025-01-01', 'end_date': '2026-06-17'},
    'executive_insights': {
        'dominant_customer': 'FARMACIAS DE SIMILARES SA DE CV',
        'top_customer_share': 42.2,
        'dominant_product': 'ARISTOCAPS-RB',
        'top_product_share': 42.1,
    },
}

def test_build_analytics_governance() -> None:
    service = GovernanceService()
    governance = service.build_analytics_governance(_SNAPSHOT)
    assert governance.source_type == 'analytics'
    assert 'venta_lineas' in governance.source_tables
    assert governance.confidence_level == 'HIGH'
    assert governance.records_analyzed == 100
    assert governance.snapshot_date == '2026-06-17'
    assert governance.evidence

def test_build_document_governance() -> None:
    service = GovernanceService()
    governance = service.build_document_governance(
        {'total_matches': 2, 'top_document': 'Manual.pdf'},
        {'average_score': 0.91, 'source_documents': ['Manual.pdf']},
    )
    assert governance.source_type == 'documents'
    assert governance.confidence_level == 'HIGH'
    assert governance.source_documents == ['Manual.pdf']

def test_build_memory_governance() -> None:
    service = GovernanceService()
    governance = service.build_memory_governance(
        {
            'latest_snapshot': {'snapshot_date': '2026-06-17', 'total_customers': 100, 'total_revenue': '49722777.13', 'top_customer': 'SIMILARES'},
            'previous_snapshot': None,
            'memory_insights': {'stable_findings': ['Primer snapshot'], 'changes': [], 'new_findings': []},
        },
        snapshot_count=1,
    )
    assert governance.source_type == 'memory'
    assert governance.confidence_level == 'MEDIUM'
    assert governance.limitations
