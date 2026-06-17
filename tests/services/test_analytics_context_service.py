from decimal import Decimal
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.models import cliente, venta, venta_linea
from app.models.cliente import Cliente
from app.models.venta import Venta
from app.models.venta_linea import VentaLinea
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService
from app.services.financial_analytics_service import FinancialAnalyticsService

@pytest.fixture
def analytics_context_service() -> AnalyticsContextService:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    session.add_all([
        Cliente(dynamics_id='C001', nombre='Alpha Corp'),
        Cliente(dynamics_id='C002', nombre='Beta SA'),
    ])
    session.add(Venta(dynamics_id='SO-001', cliente_dynamics_id='C001', monto=Decimal('0'), fecha=date(2025, 6, 1), estado='Open'))
    session.add_all([
        VentaLinea(
            sales_order_number='SO-001',
            line_creation_sequence_number=1,
            cliente_dynamics_id='C001',
            product_number='P1',
            product_name='Producto Alpha',
            ordered_sales_quantity=Decimal('1'),
            sales_price=Decimal('1000'),
            line_amount=Decimal('1000'),
            sales_order_line_status='Invoiced',
            currency_code='MXN',
            fecha=date(2025, 6, 1),
        ),
        VentaLinea(
            sales_order_number='SO-002',
            line_creation_sequence_number=1,
            cliente_dynamics_id='C002',
            product_number='P2',
            product_name='Producto Beta',
            ordered_sales_quantity=Decimal('1'),
            sales_price=Decimal('3000'),
            line_amount=Decimal('3000'),
            sales_order_line_status='Invoiced',
            currency_code='MXN',
            fecha=date(2025, 6, 2),
        ),
    ])
    session.commit()
    analytics_service = AnalyticsService(AnalyticsRepository(session))
    financial_service = FinancialAnalyticsService(FinancialAnalyticsRepository(session))
    return AnalyticsContextService(analytics_service, financial_service, top_customers_limit=3)

def test_build_snapshot_contains_financials(analytics_context_service: AnalyticsContextService) -> None:
    payload = analytics_context_service.build_snapshot().to_dict()
    assert payload['financials']['total_revenue'] == '4000.00'
    assert payload['financials']['average_order_value'] == '2000.00'
    assert payload['financials']['top_products'][0]['product_name'] == 'Producto Beta'
    assert payload['financials']['top_customers_by_revenue'][0]['customer_name'] == 'Beta SA'
    assert payload['insights']['largest_customer_share'] == pytest.approx(75.0, rel=0.01)

def test_build_snapshot_keeps_legacy_sections(analytics_context_service: AnalyticsContextService) -> None:
    payload = analytics_context_service.build_snapshot().to_dict()
    assert 'summary' in payload
    assert 'sales_by_status' in payload
    assert 'top_customers' in payload
    assert 'date_range' in payload
    assert 'insights' in payload
