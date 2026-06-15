"""
Servicio de consultas empresariales (analytics).

Orquesta métricas de ventas consumiendo repositorios desacoplados.
"""

from datetime import date

from app.domain.analytics import ClienteVentas, TotalVentasMes
from app.repositories.protocols import AnalyticsRepositoryProtocol


class AnalyticsService:
    """Consultas analíticas sobre datos sincronizados de Dynamics 365."""

    def __init__(self, repository: AnalyticsRepositoryProtocol):
        self._repository = repository

    def total_ventas_mes(
        self,
        year: int | None = None,
        month: int | None = None,
    ) -> TotalVentasMes:
        """
        Calcula el total de ventas del mes.

        Args:
            year: Año calendario. Por defecto, año actual.
            month: Mes calendario (1-12). Por defecto, mes actual.

        Returns:
            TotalVentasMes con monto agregado y cantidad de ventas.
        """
        today = date.today()
        target_year = year if year is not None else today.year
        target_month = month if month is not None else today.month
        return self._repository.total_ventas_mes(target_year, target_month)

    def ventas_por_cliente(self) -> list[ClienteVentas]:
        """
        Retorna ventas agrupadas por cliente ordenadas por monto descendente.

        Returns:
            Lista de ClienteVentas con totales por cliente.
        """
        return self._repository.ventas_por_cliente()

    def top_clientes(self, limit: int = 10) -> list[ClienteVentas]:
        """
        Retorna los clientes con mayor volumen de ventas.

        Args:
            limit: Cantidad máxima de clientes a retornar.

        Returns:
            Lista de ClienteVentas limitada al top N.
        """
        return self._repository.top_clientes(limit)

    def count_clientes(self) -> int:
        """Retorna el total de clientes registrados en PostgreSQL."""
        return self._repository.count_clientes()
