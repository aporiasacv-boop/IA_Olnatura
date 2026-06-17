from decimal import Decimal
from app.domain.financial_analytics import (
    FinancialSummary,
    ProductSales,
    SalesByLineStatus,
    TopCustomerRevenue,
    TopProductRevenue,
)
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository

class FinancialAnalyticsService:

    def __init__(self, repository: FinancialAnalyticsRepository):
        self._repository = repository

    def financial_summary(self) -> FinancialSummary:
        return self._repository.financial_summary()

    def total_revenue(self) -> Decimal:
        return self._repository.total_revenue()

    def top_customers_by_revenue(self, limit: int = 10) -> list[TopCustomerRevenue]:
        return self._repository.top_customers_by_revenue(limit)

    def top_products_by_revenue(self, limit: int = 10) -> list[TopProductRevenue]:
        return self._repository.top_products_by_revenue(limit)

    def sales_by_line_status(self) -> list[SalesByLineStatus]:
        return self._repository.sales_by_line_status()

    def sales_by_product(self) -> list[ProductSales]:
        return self._repository.sales_by_product()

    def count_lines(self) -> int:
        return self._repository.count_lines()
