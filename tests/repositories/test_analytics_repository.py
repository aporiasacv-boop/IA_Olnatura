"""
Pruebas unitarias del repositorio analítico.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository


def test_total_ventas_mes_sums_sales_in_period(analytics_db: Session) -> None:
    """Verifica suma de ventas del mes junio 2025."""
    repo = AnalyticsRepository(analytics_db)
    result = repo.total_ventas_mes(year=2025, month=6)

    assert result.year == 2025
    assert result.month == 6
    assert result.total == Decimal("4500.00")
    assert result.cantidad_ventas == 3


def test_total_ventas_mes_returns_zero_when_no_sales(analytics_db: Session) -> None:
    """Verifica cero ventas en mes sin registros."""
    repo = AnalyticsRepository(analytics_db)
    result = repo.total_ventas_mes(year=2024, month=1)

    assert result.total == Decimal("0")
    assert result.cantidad_ventas == 0


def test_ventas_por_cliente_groups_and_orders(analytics_db: Session) -> None:
    """Verifica agrupación por cliente ordenada por monto descendente."""
    repo = AnalyticsRepository(analytics_db)
    result = repo.ventas_por_cliente()

    assert len(result) == 3
    assert result[0].cliente_dynamics_id == "C002"
    assert result[0].total_ventas == Decimal("3800.00")
    assert result[0].cantidad_ventas == 2
    assert result[1].cliente_dynamics_id == "C001"
    assert result[1].total_ventas == Decimal("1500.00")


def test_top_clientes_respects_limit(analytics_db: Session) -> None:
    """Verifica que top_clientes limita resultados."""
    repo = AnalyticsRepository(analytics_db)
    result = repo.top_clientes(limit=2)

    assert len(result) == 2
    assert result[0].cliente_dynamics_id == "C002"
    assert result[1].cliente_dynamics_id == "C001"
