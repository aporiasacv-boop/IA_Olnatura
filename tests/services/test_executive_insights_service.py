from decimal import Decimal

import pytest

from app.domain.executive_insights import ExecutiveInsights
from app.services.executive_insights_service import ExecutiveInsightsService

@pytest.fixture
def service() -> ExecutiveInsightsService:
    return ExecutiveInsightsService()

def _financials(
    total_revenue: str = '10000.00',
    customer_revenues: list[str] | None = None,
    product_revenues: list[str] | None = None,
    sales_by_status: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    customer_revenues = customer_revenues or ['6000.00', '2000.00', '1000.00']
    product_revenues = product_revenues or ['5500.00', '2500.00']
    return {
        'total_revenue': total_revenue,
        'top_customers_by_revenue': [
            {
                'customer_account': f'C00{i + 1}',
                'customer_name': f'Cliente {i + 1}',
                'lines': 1,
                'total_revenue': revenue,
            }
            for i, revenue in enumerate(customer_revenues)
        ],
        'top_products': [
            {
                'product_number': f'P{i + 1}',
                'product_name': f'Producto {i + 1}',
                'lines': 1,
                'total_revenue': revenue,
            }
            for i, revenue in enumerate(product_revenues)
        ],
        'sales_by_status': sales_by_status or [
            {'status': 'Invoiced', 'count': 8, 'total_revenue': '8000.00'},
            {'status': 'Open', 'count': 2, 'total_revenue': '2000.00'},
        ],
    }

def test_build_from_financials_calculates_shares(service: ExecutiveInsightsService) -> None:
    insights = service.build_from_financials(_financials())
    assert insights.top_customer_share == pytest.approx(60.0, rel=0.01)
    assert insights.top_5_customer_share == pytest.approx(90.0, rel=0.01)
    assert insights.top_product_share == pytest.approx(55.0, rel=0.01)
    assert insights.dominant_customer == 'Cliente 1'
    assert insights.dominant_product == 'Producto 1'
    assert insights.invoice_rate == pytest.approx(80.0, rel=0.01)
    assert insights.revenue_concentration == 'Alta concentracion comercial'

def test_high_customer_dependency_risk_flag(service: ExecutiveInsightsService) -> None:
    financials = _financials(customer_revenues=['6000.00', '1000.00'])
    insights = service.build_from_financials(financials)
    assert 'Alta dependencia comercial de un solo cliente' in insights.risk_flags

def test_moderate_customer_concentration_risk_flag(service: ExecutiveInsightsService) -> None:
    financials = _financials(customer_revenues=['4000.00', '2000.00', '1000.00'])
    insights = service.build_from_financials(financials)
    assert 'Concentracion comercial moderada' in insights.risk_flags
    assert insights.revenue_concentration == 'Concentracion comercial moderada'

def test_high_product_dependency_risk_flag(service: ExecutiveInsightsService) -> None:
    financials = _financials(product_revenues=['6000.00', '1000.00'])
    insights = service.build_from_financials(financials)
    assert 'Alta dependencia de un solo producto' in insights.risk_flags

def test_pending_invoice_risk_flag(service: ExecutiveInsightsService) -> None:
    financials = _financials(sales_by_status=[
        {'status': 'Invoiced', 'count': 5, 'total_revenue': '5000.00'},
        {'status': 'Open', 'count': 5, 'total_revenue': '5000.00'},
    ])
    insights = service.build_from_financials(financials)
    assert insights.invoice_rate == pytest.approx(50.0, rel=0.01)
    assert 'Existen pedidos pendientes de facturacion' in insights.risk_flags

def test_fully_invoiced_has_no_pending_risk(service: ExecutiveInsightsService) -> None:
    financials = _financials(sales_by_status=[
        {'status': 'Invoiced', 'count': 10, 'total_revenue': '10000.00'},
    ])
    insights = service.build_from_financials(financials)
    assert insights.invoice_rate == 100.0
    assert service.is_fully_invoiced(insights) is True
    assert 'Existen pedidos pendientes de facturacion' not in insights.risk_flags

def test_to_dict_serializes_risk_flags(service: ExecutiveInsightsService) -> None:
    insights = service.build_from_financials(_financials(customer_revenues=['6000.00']))
    payload = insights.to_dict()
    assert payload['dominant_customer'] == 'Cliente 1'
    assert isinstance(payload['risk_flags'], list)
