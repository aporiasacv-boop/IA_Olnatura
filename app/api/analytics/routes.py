from fastapi import APIRouter, Depends, Query
from app.api.deps import get_analytics_service
from app.schemas.analytics import (
    ClienteVentasResponse,
    CustomersCountResponse,
    SalesByStatusItemResponse,
    SalesCountResponse,
    SalesSummaryResponse,
    TopClientesResponse,
    TopCustomerResponse,
    TotalVentasMesResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get('/customers/count', response_model=CustomersCountResponse, summary='Total de clientes sincronizados', tags=['Analytics'])
def get_customers_count(service: AnalyticsService=Depends(get_analytics_service)) -> CustomersCountResponse:
    return CustomersCountResponse(total_customers=service.count_clientes())

@router.get('/sales/count', response_model=SalesCountResponse, summary='Total de pedidos de venta sincronizados', tags=['Analytics'])
def get_sales_count(service: AnalyticsService=Depends(get_analytics_service)) -> SalesCountResponse:
    return SalesCountResponse(total_sales_orders=service.count_sales_orders())

@router.get('/sales/summary', response_model=SalesSummaryResponse, summary='Resumen agregado de ventas', tags=['Analytics'])
def get_sales_summary(service: AnalyticsService=Depends(get_analytics_service)) -> SalesSummaryResponse:
    summary = service.sales_summary()
    return SalesSummaryResponse(total_orders=summary.total_orders, total_amount=summary.total_amount, average_order_amount=summary.average_order_amount)

@router.get('/sales/by-status', response_model=list[SalesByStatusItemResponse], summary='Pedidos de venta agrupados por estado', tags=['Analytics'])
def get_sales_by_status(service: AnalyticsService=Depends(get_analytics_service)) -> list[SalesByStatusItemResponse]:
    return [SalesByStatusItemResponse(status=item.status, count=item.count) for item in service.sales_by_status()]

@router.get('/sales/month', response_model=TotalVentasMesResponse, summary='Total de ventas del mes', tags=['Analytics'])
def get_sales_month(year: int | None=Query(None, ge=2000, le=2100, description='Año (default: actual)'), month: int | None=Query(None, ge=1, le=12, description='Mes 1-12 (default: actual)'), service: AnalyticsService=Depends(get_analytics_service)) -> TotalVentasMesResponse:
    result = service.total_ventas_mes(year=year, month=month)
    return TotalVentasMesResponse(year=result.year, month=result.month, total=result.total, cantidad_ventas=result.cantidad_ventas)

@router.get('/top-customers', response_model=list[TopCustomerResponse], summary='Top clientes por monto de pedidos', tags=['Analytics'])
def get_top_customers(limit: int=Query(10, ge=1, le=100, description='Cantidad de clientes a retornar'), service: AnalyticsService=Depends(get_analytics_service)) -> list[TopCustomerResponse]:
    return [TopCustomerResponse(customer_account=item.customer_account, customer_name=item.customer_name, orders=item.orders, total_amount=item.total_amount) for item in service.top_customers(limit=limit)]

@router.get('/reports/top-customers', response_model=TopClientesResponse, summary='Top clientes (formato legado)', tags=['Analytics'])
def get_top_customers_legacy(limit: int=Query(10, ge=1, le=100, description='Cantidad de clientes a retornar'), service: AnalyticsService=Depends(get_analytics_service)) -> TopClientesResponse:
    clientes = service.top_clientes(limit=limit)
    return TopClientesResponse(limit=limit, clientes=[ClienteVentasResponse(cliente_dynamics_id=c.cliente_dynamics_id, nombre=c.nombre, total_ventas=c.total_ventas, cantidad_ventas=c.cantidad_ventas) for c in clientes])
