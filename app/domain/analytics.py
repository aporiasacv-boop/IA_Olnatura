"""
Modelos de dominio para consultas analíticas.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TotalVentasMes:
    """Total de ventas agregadas por mes."""

    year: int
    month: int
    total: Decimal
    cantidad_ventas: int


@dataclass(frozen=True)
class ClienteVentas:
    """Ventas agregadas por cliente."""

    cliente_dynamics_id: str
    nombre: str | None
    total_ventas: Decimal
    cantidad_ventas: int
