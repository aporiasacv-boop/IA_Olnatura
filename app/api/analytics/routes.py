"""
Endpoints de consultas empresariales (analytics).
"""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_analytics_service
from app.schemas.analytics import (
    ClienteVentasResponse,
    TopClientesResponse,
    TotalVentasMesResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get(
    "/sales/month",
    response_model=TotalVentasMesResponse,
    summary="Total de ventas del mes",
    tags=["Analytics"],
)
def get_sales_month(
    year: int | None = Query(None, ge=2000, le=2100, description="Año (default: actual)"),
    month: int | None = Query(None, ge=1, le=12, description="Mes 1-12 (default: actual)"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> TotalVentasMesResponse:
    """Retorna el monto total y cantidad de ventas del mes indicado."""
    result = service.total_ventas_mes(year=year, month=month)
    return TotalVentasMesResponse(
        year=result.year,
        month=result.month,
        total=result.total,
        cantidad_ventas=result.cantidad_ventas,
    )


@router.get(
    "/top-customers",
    response_model=TopClientesResponse,
    summary="Top clientes por volumen de ventas",
    tags=["Analytics"],
)
def get_top_customers(
    limit: int = Query(10, ge=1, le=100, description="Cantidad de clientes a retornar"),
    service: AnalyticsService = Depends(get_analytics_service),
) -> TopClientesResponse:
    """Retorna los clientes con mayor monto total de ventas."""
    clientes = service.top_clientes(limit=limit)
    return TopClientesResponse(
        limit=limit,
        clientes=[
            ClienteVentasResponse(
                cliente_dynamics_id=c.cliente_dynamics_id,
                nombre=c.nombre,
                total_ventas=c.total_ventas,
                cantidad_ventas=c.cantidad_ventas,
            )
            for c in clientes
        ],
    )
