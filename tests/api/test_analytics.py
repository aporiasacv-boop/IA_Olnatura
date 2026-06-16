from collections.abc import Generator
from decimal import Decimal
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.api.deps import get_analytics_service, get_db
from app.domain.analytics import ClienteVentas, SalesByStatus, SalesSummary, TopCustomer, TotalVentasMes
from app.main import app
from app.services.analytics_service import AnalyticsService

@pytest.fixture
def analytics_client(analytics_db: Session) -> Generator[TestClient, None, None]:

    def override_get_db() -> Generator[Session, None, None]:
        yield analytics_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_get_customers_count_endpoint(analytics_client: TestClient) -> None:
    response = analytics_client.get('/analytics/customers/count')
    assert response.status_code == 200
    assert response.json() == {'total_customers': 3}

def test_get_sales_count_endpoint(analytics_client: TestClient) -> None:
    response = analytics_client.get('/analytics/sales/count')
    assert response.status_code == 200
    assert response.json() == {'total_sales_orders': 5}

def test_get_sales_summary_endpoint(analytics_client: TestClient) -> None:
    response = analytics_client.get('/analytics/sales/summary')
    assert response.status_code == 200
    data = response.json()
    assert data['total_orders'] == 5
    assert Decimal(data['total_amount']) == Decimal('5500.00')
    assert Decimal(data['average_order_amount']) == Decimal('1100.00')

def test_get_sales_by_status_endpoint(analytics_client: TestClient) -> None:
    response = analytics_client.get('/analytics/sales/by-status')
    assert response.status_code == 200
    statuses = {item['status']: item['count'] for item in response.json()}
    assert statuses['Open'] == 2
    assert statuses['Delivered'] == 1
    assert statuses['Closed'] == 1
    assert statuses['Draft'] == 1

def test_get_sales_month_endpoint(analytics_client: TestClient) -> None:
    response = analytics_client.get('/analytics/sales/month', params={'year': 2025, 'month': 6})
    assert response.status_code == 200
    data = response.json()
    assert data['year'] == 2025
    assert data['month'] == 6
    assert Decimal(data['total']) == Decimal('4500.00')
    assert data['cantidad_ventas'] == 3

def test_get_top_customers_endpoint(analytics_client: TestClient) -> None:
    response = analytics_client.get('/analytics/top-customers', params={'limit': 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['customer_account'] == 'C002'
    assert data[0]['customer_name'] == 'Beta SA'
    assert data[0]['orders'] == 2
    assert Decimal(data[0]['total_amount']) == Decimal('3800.00')

def test_get_top_customers_legacy_endpoint(analytics_client: TestClient) -> None:
    response = analytics_client.get('/analytics/reports/top-customers', params={'limit': 2})
    assert response.status_code == 200
    data = response.json()
    assert data['limit'] == 2
    assert len(data['clientes']) == 2
    assert data['clientes'][0]['cliente_dynamics_id'] == 'C002'

def test_get_sales_month_with_mocked_service() -> None:
    mock_service = MagicMock(spec=AnalyticsService)
    mock_service.total_ventas_mes.return_value = TotalVentasMes(year=2025, month=1, total=Decimal('100.00'), cantidad_ventas=1)
    app.dependency_overrides[get_analytics_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/analytics/sales/month', params={'year': 2025, 'month': 1})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()['total'] == '100.00'
    mock_service.total_ventas_mes.assert_called_once_with(year=2025, month=1)

def test_get_sales_summary_with_mocked_service() -> None:
    mock_service = MagicMock(spec=AnalyticsService)
    mock_service.sales_summary.return_value = SalesSummary(total_orders=10, total_amount=Decimal('5000.00'), average_order_amount=Decimal('500.00'))
    app.dependency_overrides[get_analytics_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/analytics/sales/summary')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()['total_orders'] == 10
    mock_service.sales_summary.assert_called_once()
