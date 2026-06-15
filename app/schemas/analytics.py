"""
Schemas de respuesta para endpoints analíticos.
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class TotalVentasMesResponse(BaseModel):
    """Total de ventas de un mes calendario."""

    year: int = Field(..., description="Año consultado")
    month: int = Field(..., description="Mes consultado (1-12)")
    total: Decimal = Field(..., description="Monto total de ventas")
    cantidad_ventas: int = Field(..., description="Número de ventas en el periodo")


class ClienteVentasResponse(BaseModel):
    """Ventas agregadas por cliente."""

    cliente_dynamics_id: str = Field(..., description="ID del cliente en Dynamics")
    nombre: str | None = Field(None, description="Nombre del cliente")
    total_ventas: Decimal = Field(..., description="Monto total acumulado")
    cantidad_ventas: int = Field(..., description="Número de ventas del cliente")


class TopClientesResponse(BaseModel):
    """Listado de clientes con mayor volumen de ventas."""

    limit: int = Field(..., description="Límite aplicado a la consulta")
    clientes: list[ClienteVentasResponse] = Field(default_factory=list)
