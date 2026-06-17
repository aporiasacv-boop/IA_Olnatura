from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class FinancialSummary:
    total_revenue: Decimal
    total_lines: int
    total_orders: int
    average_order_value: Decimal

@dataclass(frozen=True)
class TopCustomerRevenue:
    customer_account: str | None
    customer_name: str | None
    lines: int
    total_revenue: Decimal

@dataclass(frozen=True)
class TopProductRevenue:
    product_number: str | None
    product_name: str | None
    lines: int
    total_revenue: Decimal

@dataclass(frozen=True)
class SalesByLineStatus:
    status: str
    count: int
    total_revenue: Decimal

@dataclass(frozen=True)
class ProductSales:
    product_number: str | None
    product_name: str | None
    total_revenue: Decimal
    total_quantity: Decimal
