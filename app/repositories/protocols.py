from typing import Protocol
from app.domain.analytics import ClienteVentas, SalesByStatus, SalesSummary, TopCustomer, TotalVentasMes

class AnalyticsRepositoryProtocol(Protocol):

    def total_ventas_mes(self, year: int, month: int) -> TotalVentasMes:
        ...

    def ventas_por_cliente(self) -> list[ClienteVentas]:
        ...

    def top_clientes(self, limit: int) -> list[ClienteVentas]:
        ...

    def count_clientes(self) -> int:
        ...

    def count_ventas(self) -> int:
        ...

    def sales_summary(self) -> SalesSummary:
        ...

    def sales_by_status(self) -> list[SalesByStatus]:
        ...

    def top_customers(self, limit: int) -> list[TopCustomer]:
        ...
