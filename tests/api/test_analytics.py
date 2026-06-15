"""
Pruebas unitarias de endpoints analíticos.
"""

from collections.abc import Generator
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_analytics_service, get_db
from app.domain.analytics import ClienteVentas, TotalVentasMes
from app.main import app
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def analytics_client(analytics_db: Session) -> Generator[TestClient, None, None]:
    """Cliente HTTP con BD SQLite y servicio analítico real."""

    def override_get_db() -> Generator[Session, None, None]:
        yield analytics_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_get_sales_month_endpoint(analytics_client: TestClient) -> None:
    """Verifica GET /analytics/sales/month con datos reales."""
    response = analytics_client.get("/analytics/sales/month", params={"year": 2025, "month": 6})

    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2025
    assert data["month"] == 6
    assert Decimal(data["total"]) == Decimal("4500.00")
    assert data["cantidad_ventas"] == 3


def test_get_top_customers_endpoint(analytics_client: TestClient) -> None:
    """Verifica GET /analytics/top-customers con datos reales."""
    response = analytics_client.get("/analytics/top-customers", params={"limit": 2})

    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert len(data["clientes"]) == 2
    assert data["clientes"][0]["cliente_dynamics_id"] == "C002"
    assert data["clientes"][0]["nombre"] == "Beta SA"


def test_get_sales_month_with_mocked_service() -> None:
    """Verifica endpoint con servicio mockeado (desacoplado del repositorio)."""
    mock_service = MagicMock(spec=AnalyticsService)
    mock_service.total_ventas_mes.return_value = TotalVentasMes(
        year=2025,
        month=1,
        total=Decimal("100.00"),
        cantidad_ventas=1,
    )

    app.dependency_overrides[get_analytics_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get("/analytics/sales/month", params={"year": 2025, "month": 1})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total"] == "100.00"
    mock_service.total_ventas_mes.assert_called_once_with(year=2025, month=1)
