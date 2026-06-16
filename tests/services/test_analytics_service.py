from decimal import Decimal
from unittest.mock import MagicMock
from app.domain.analytics import ClienteVentas, SalesByStatus, SalesSummary, TopCustomer, TotalVentasMes
from app.services.analytics_service import AnalyticsService

def test_total_ventas_mes_delegates_to_repository() -> None:
    repository = MagicMock()
    repository.total_ventas_mes.return_value = TotalVentasMes(year=2025, month=6, total=Decimal('4500.00'), cantidad_ventas=3)
    service = AnalyticsService(repository)
    result = service.total_ventas_mes(year=2025, month=6)
    assert result.total == Decimal('4500.00')
    repository.total_ventas_mes.assert_called_once_with(2025, 6)

def test_ventas_por_cliente_delegates_to_repository() -> None:
    repository = MagicMock()
    repository.ventas_por_cliente.return_value = [ClienteVentas('C001', 'Alpha', Decimal('1500'), 2)]
    service = AnalyticsService(repository)
    result = service.ventas_por_cliente()
    assert len(result) == 1
    repository.ventas_por_cliente.assert_called_once()

def test_top_clientes_delegates_with_limit() -> None:
    repository = MagicMock()
    repository.top_clientes.return_value = [ClienteVentas('C002', 'Beta', Decimal('3800'), 2)]
    service = AnalyticsService(repository)
    result = service.top_clientes(limit=5)
    assert result[0].cliente_dynamics_id == 'C002'
    repository.top_clientes.assert_called_once_with(5)

def test_count_clientes_delegates_to_repository() -> None:
    repository = MagicMock()
    repository.count_clientes.return_value = 42
    service = AnalyticsService(repository)
    assert service.count_clientes() == 42
    repository.count_clientes.assert_called_once()

def test_count_sales_orders_delegates_to_repository() -> None:
    repository = MagicMock()
    repository.count_ventas.return_value = 100
    service = AnalyticsService(repository)
    assert service.count_sales_orders() == 100
    repository.count_ventas.assert_called_once()

def test_sales_summary_delegates_to_repository() -> None:
    repository = MagicMock()
    repository.sales_summary.return_value = SalesSummary(total_orders=5, total_amount=Decimal('5500.00'), average_order_amount=Decimal('1100.00'))
    service = AnalyticsService(repository)
    result = service.sales_summary()
    assert result.total_orders == 5
    repository.sales_summary.assert_called_once()

def test_sales_by_status_delegates_to_repository() -> None:
    repository = MagicMock()
    repository.sales_by_status.return_value = [SalesByStatus(status='Open', count=2)]
    service = AnalyticsService(repository)
    result = service.sales_by_status()
    assert result[0].status == 'Open'
    repository.sales_by_status.assert_called_once()

def test_top_customers_delegates_with_limit() -> None:
    repository = MagicMock()
    repository.top_customers.return_value = [TopCustomer('C002', 'Beta SA', 2, Decimal('3800.00'))]
    service = AnalyticsService(repository)
    result = service.top_customers(limit=10)
    assert result[0].customer_account == 'C002'
    repository.top_customers.assert_called_once_with(10)
