from decimal import Decimal
from sqlalchemy.orm import Session
from app.repositories.analytics_repository import AnalyticsRepository

def test_total_ventas_mes_sums_sales_in_period(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    result = repo.total_ventas_mes(year=2025, month=6)
    assert result.year == 2025
    assert result.month == 6
    assert result.total == Decimal('4500.00')
    assert result.cantidad_ventas == 3

def test_total_ventas_mes_returns_zero_when_no_sales(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    result = repo.total_ventas_mes(year=2024, month=1)
    assert result.total == Decimal('0')
    assert result.cantidad_ventas == 0

def test_ventas_por_cliente_groups_and_orders(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    result = repo.ventas_por_cliente()
    assert len(result) == 3
    assert result[0].cliente_dynamics_id == 'C002'
    assert result[0].total_ventas == Decimal('3800.00')
    assert result[0].cantidad_ventas == 2

def test_top_clientes_respects_limit(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    result = repo.top_clientes(limit=2)
    assert len(result) == 2
    assert result[0].cliente_dynamics_id == 'C002'
    assert result[1].cliente_dynamics_id == 'C001'

def test_count_clientes_returns_total(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    assert repo.count_clientes() == 3

def test_count_ventas_returns_total(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    assert repo.count_ventas() == 5

def test_sales_summary_aggregates_orders(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    result = repo.sales_summary()
    assert result.total_orders == 5
    assert result.total_amount == Decimal('5500.00')
    assert result.average_order_amount == Decimal('1100.00')

def test_sales_by_status_groups_orders(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    result = repo.sales_by_status()
    statuses = {item.status: item.count for item in result}
    assert statuses['Open'] == 2
    assert statuses['Delivered'] == 1
    assert statuses['Closed'] == 1
    assert statuses['Draft'] == 1

def test_top_customers_respects_limit(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    result = repo.top_customers(limit=2)
    assert len(result) == 2
    assert result[0].customer_account == 'C002'
    assert result[0].customer_name == 'Beta SA'
    assert result[0].orders == 2
    assert result[0].total_amount == Decimal('3800.00')

def test_top_customers_returns_empty_for_zero_limit(analytics_db: Session) -> None:
    repo = AnalyticsRepository(analytics_db)
    assert repo.top_customers(limit=0) == []

def test_sales_date_range_returns_min_and_max(analytics_db: Session) -> None:
    from datetime import date
    repo = AnalyticsRepository(analytics_db)
    start_date, end_date = repo.sales_date_range()
    assert start_date == date(2025, 5, 20)
    assert end_date == date(2025, 6, 15)
