from datetime import date
from app.domain.analytics import ClienteVentas, SalesByStatus, SalesSummary, TopCustomer, TotalVentasMes
from app.repositories.protocols import AnalyticsRepositoryProtocol

class AnalyticsService:

    def __init__(self, repository: AnalyticsRepositoryProtocol):
        self._repository = repository

    def total_ventas_mes(self, year: int | None=None, month: int | None=None) -> TotalVentasMes:
        today = date.today()
        target_year = year if year is not None else today.year
        target_month = month if month is not None else today.month
        return self._repository.total_ventas_mes(target_year, target_month)

    def ventas_por_cliente(self) -> list[ClienteVentas]:
        return self._repository.ventas_por_cliente()

    def top_clientes(self, limit: int=10) -> list[ClienteVentas]:
        return self._repository.top_clientes(limit)

    def count_clientes(self) -> int:
        return self._repository.count_clientes()

    def count_sales_orders(self) -> int:
        return self._repository.count_ventas()

    def sales_summary(self) -> SalesSummary:
        return self._repository.sales_summary()

    def sales_by_status(self) -> list[SalesByStatus]:
        return self._repository.sales_by_status()

    def top_customers(self, limit: int=10) -> list[TopCustomer]:
        return self._repository.top_customers(limit)
