"""
Contratos de repositorios desacoplados.

Define protocolos que los servicios consumen sin depender
de implementaciones concretas de acceso a datos.
"""

from decimal import Decimal
from typing import Protocol

from app.domain.analytics import ClienteVentas, TotalVentasMes


class AnalyticsRepositoryProtocol(Protocol):
    """Contrato para consultas analíticas sobre ventas y clientes."""

    def total_ventas_mes(self, year: int, month: int) -> TotalVentasMes:
        """Calcula el total de ventas para un año y mes."""
        ...

    def ventas_por_cliente(self) -> list[ClienteVentas]:
        """Agrupa ventas por cliente con totales acumulados."""
        ...

    def top_clientes(self, limit: int) -> list[ClienteVentas]:
        """Retorna los clientes con mayor volumen de ventas."""
        ...

    def count_clientes(self) -> int:
        """Retorna el total de clientes registrados."""
        ...
