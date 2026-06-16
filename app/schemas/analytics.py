from decimal import Decimal
from typing import Any
from pydantic import BaseModel, Field

class TotalVentasMesResponse(BaseModel):
    year: int = Field(..., description='Año consultado')
    month: int = Field(..., description='Mes consultado (1-12)')
    total: Decimal = Field(..., description='Monto total de ventas')
    cantidad_ventas: int = Field(..., description='Número de ventas en el periodo')

class ClienteVentasResponse(BaseModel):
    cliente_dynamics_id: str = Field(..., description='ID del cliente en Dynamics')
    nombre: str | None = Field(None, description='Nombre del cliente')
    total_ventas: Decimal = Field(..., description='Monto total acumulado')
    cantidad_ventas: int = Field(..., description='Número de ventas del cliente')

class TopClientesResponse(BaseModel):
    limit: int = Field(..., description='Límite aplicado a la consulta')
    clientes: list[ClienteVentasResponse] = Field(default_factory=list)

class CustomersCountResponse(BaseModel):
    total_customers: int = Field(..., description='Cantidad de clientes en PostgreSQL')

class SalesCountResponse(BaseModel):
    total_sales_orders: int = Field(..., description='Cantidad de pedidos en PostgreSQL')

class SalesSummaryResponse(BaseModel):
    total_orders: int = Field(..., description='Número total de pedidos')
    total_amount: Decimal = Field(..., description='Monto total acumulado')
    average_order_amount: Decimal = Field(..., description='Ticket promedio por pedido')

class SalesByStatusItemResponse(BaseModel):
    status: str = Field(..., description='Estado del pedido en Dynamics')
    count: int = Field(..., description='Cantidad de pedidos en ese estado')

class TopCustomerResponse(BaseModel):
    customer_account: str = Field(..., description='Cuenta del cliente')
    customer_name: str | None = Field(None, description='Nombre del cliente')
    orders: int = Field(..., description='Cantidad de pedidos del cliente')
    total_amount: Decimal = Field(..., description='Monto total acumulado')
