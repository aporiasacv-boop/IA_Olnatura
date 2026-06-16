from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class TotalVentasMes:
    year: int
    month: int
    total: Decimal
    cantidad_ventas: int

@dataclass(frozen=True)
class ClienteVentas:
    cliente_dynamics_id: str
    nombre: str | None
    total_ventas: Decimal
    cantidad_ventas: int

@dataclass(frozen=True)
class SalesSummary:
    total_orders: int
    total_amount: Decimal
    average_order_amount: Decimal

@dataclass(frozen=True)
class SalesByStatus:
    status: str
    count: int

@dataclass(frozen=True)
class TopCustomer:
    customer_account: str
    customer_name: str | None
    orders: int
    total_amount: Decimal
