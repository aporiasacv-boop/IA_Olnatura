from dataclasses import dataclass
from typing import Any

from app.domain.executive_insights import ExecutiveInsights

@dataclass(frozen=True)
class AnalyticsDateRange:
    start_date: str | None
    end_date: str | None

    def to_dict(self) -> dict[str, str | None]:
        return {'start_date': self.start_date, 'end_date': self.end_date}

@dataclass(frozen=True)
class CustomerConcentration:
    top_5_share: float
    customers_with_sales: int
    leading_customer: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            'top_5_share': self.top_5_share,
            'customers_with_sales': self.customers_with_sales,
            'leading_customer': self.leading_customer,
        }

@dataclass(frozen=True)
class AnalyticsInsights:
    largest_customer_share: float
    customer_concentration: CustomerConcentration

    def to_dict(self) -> dict[str, Any]:
        return {
            'largest_customer_share': self.largest_customer_share,
            'customer_concentration': self.customer_concentration.to_dict(),
        }

@dataclass(frozen=True)
class AnalyticsContextSnapshot:
    summary: dict[str, Any]
    sales_by_status: list[dict[str, Any]]
    top_customers: list[dict[str, Any]]
    date_range: AnalyticsDateRange
    insights: AnalyticsInsights
    financials: dict[str, Any]
    executive_insights: ExecutiveInsights

    def to_dict(self) -> dict[str, Any]:
        return {
            'summary': self.summary,
            'sales_by_status': self.sales_by_status,
            'top_customers': self.top_customers,
            'date_range': self.date_range.to_dict(),
            'insights': self.insights.to_dict(),
            'financials': self.financials,
            'executive_insights': self.executive_insights.to_dict(),
        }
