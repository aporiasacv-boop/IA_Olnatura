from decimal import Decimal
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.models import cliente, venta, venta_linea
from app.models.cliente import Cliente
from app.models.venta_linea import VentaLinea
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository

@pytest.fixture
def financial_db():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    session.add(Cliente(dynamics_id='C001', nombre='Alpha Corp'))
    session.add(Cliente(dynamics_id='C002', nombre='Beta SA'))
    session.add_all([
        VentaLinea(
            sales_order_number='SO-001',
            line_creation_sequence_number=1,
            cliente_dynamics_id='C001',
            product_number='P1',
            product_name='Producto Alpha',
            ordered_sales_quantity=Decimal('10'),
            sales_price=Decimal('100'),
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
            ordered_sales_quantity=Decimal('5'),
            sales_price=Decimal('200'),
            line_amount=Decimal('3000'),
            sales_order_line_status='Invoiced',
            currency_code='MXN',
            fecha=date(2025, 6, 2),
        ),
    ])
    session.commit()
    yield session
    session.close()

def test_financial_summary_uses_line_amount(financial_db) -> None:
    repo = FinancialAnalyticsRepository(financial_db)
    summary = repo.financial_summary()
    assert summary.total_revenue == Decimal('4000')
    assert summary.total_lines == 2
    assert summary.total_orders == 2
    assert summary.average_order_value == Decimal('2000')

def test_top_customers_and_products_by_revenue(financial_db) -> None:
    repo = FinancialAnalyticsRepository(financial_db)
    top_customers = repo.top_customers_by_revenue(limit=2)
    top_products = repo.top_products_by_revenue(limit=2)
    assert top_customers[0].customer_name == 'Beta SA'
    assert top_customers[0].total_revenue == Decimal('3000')
    assert top_products[0].product_name == 'Producto Beta'
    assert top_products[0].total_revenue == Decimal('3000')

def test_sales_by_line_status(financial_db) -> None:
    repo = FinancialAnalyticsRepository(financial_db)
    statuses = repo.sales_by_line_status()
    assert statuses[0].status == 'Invoiced'
    assert statuses[0].total_revenue == Decimal('4000')
