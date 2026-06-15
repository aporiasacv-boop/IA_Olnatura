"""
Pruebas unitarias del servicio de consultas empresariales.
"""

from decimal import Decimal
from unittest.mock import MagicMock

from app.domain.analytics import ClienteVentas, TotalVentasMes
from app.services.analytics_service import AnalyticsService


def test_total_ventas_mes_delegates_to_repository() -> None:
    """Verifica delegación al repositorio con año y mes explícitos."""
    repository = MagicMock()
    repository.total_ventas_mes.return_value = TotalVentasMes(
        year=2025,
        month=6,
        total=Decimal("4500.00"),
        cantidad_ventas=3,
    )
    service = AnalyticsService(repository)

    result = service.total_ventas_mes(year=2025, month=6)

    assert result.total == Decimal("4500.00")
    repository.total_ventas_mes.assert_called_once_with(2025, 6)


def test_ventas_por_cliente_delegates_to_repository() -> None:
    """Verifica delegación de ventas_por_cliente."""
    repository = MagicMock()
    repository.ventas_por_cliente.return_value = [
        ClienteVentas("C001", "Alpha", Decimal("1500"), 2),
    ]
    service = AnalyticsService(repository)

    result = service.ventas_por_cliente()

    assert len(result) == 1
    assert result[0].nombre == "Alpha"
    repository.ventas_por_cliente.assert_called_once()


def test_top_clientes_delegates_with_limit() -> None:
    """Verifica delegación de top_clientes con límite."""
    repository = MagicMock()
    repository.top_clientes.return_value = [
        ClienteVentas("C002", "Beta", Decimal("3800"), 2),
    ]
    service = AnalyticsService(repository)

    result = service.top_clientes(limit=5)

    assert result[0].cliente_dynamics_id == "C002"
    repository.top_clientes.assert_called_once_with(5)
