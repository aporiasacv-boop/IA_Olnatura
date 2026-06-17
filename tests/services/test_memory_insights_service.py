from app.services.memory_insights_service import MemoryInsightsService

_CURRENT = {
    'total_customers': 100,
    'total_orders': 100,
    'total_revenue': '49722777.13',
    'top_customer': 'FARMACIAS DE SIMILARES SA DE CV',
    'top_customer_share': 42.2,
    'top_product': 'ARISTOCAPS-RB',
    'top_product_share': 42.1,
    'executive_insights': {'risk_flags': ['Concentracion comercial moderada']},
}

_PREVIOUS = {
    'total_customers': 100,
    'total_orders': 100,
    'total_revenue': '49722777.13',
    'top_customer': 'FARMACIAS DE SIMILARES SA DE CV',
    'top_customer_share': 42.2,
    'top_product': 'ARISTOCAPS-RB',
    'top_product_share': 42.1,
    'executive_insights': {'risk_flags': ['Concentracion comercial moderada']},
}


def test_build_insights_detects_stability() -> None:
    service = MemoryInsightsService()
    insights = service.build_insights(_CURRENT, _PREVIOUS)
    assert any('clientes permanece estable' in item.lower() for item in insights.stable_findings)
    assert any('similares' in item.lower() for item in insights.stable_findings)
    assert any('producto dominante' in item.lower() for item in insights.stable_findings)
    assert any('hallazgo persistente' in item.lower() for item in insights.stable_findings)


def test_build_insights_without_previous_snapshot() -> None:
    service = MemoryInsightsService()
    insights = service.build_insights(_CURRENT, None)
    assert insights.changes == []
    assert any('primer snapshot' in item.lower() for item in insights.stable_findings)
    assert any('cliente dominante inicial' in item.lower() for item in insights.new_findings)


def test_build_insights_detects_revenue_change() -> None:
    service = MemoryInsightsService()
    previous = dict(_PREVIOUS)
    previous['total_revenue'] = '40000000.00'
    insights = service.build_insights(_CURRENT, previous)
    assert any('ingresos' in item.lower() for item in insights.changes)
