from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domain.financial_analytics import (
    FinancialSummary,
    ProductSales,
    SalesByLineStatus,
    TopCustomerRevenue,
    TopProductRevenue,
)
from app.models.cliente import Cliente
from app.models.venta_linea import VentaLinea

class FinancialAnalyticsRepository:

    def __init__(self, db: Session):
        self._db = db

    def financial_summary(self) -> FinancialSummary:
        stmt = select(
            func.coalesce(func.sum(VentaLinea.line_amount), 0),
            func.count(VentaLinea.id),
            func.count(func.distinct(VentaLinea.sales_order_number)),
        )
        total_revenue, total_lines, total_orders = self._db.execute(stmt).one()
        total_revenue_decimal = Decimal(str(total_revenue))
        total_orders_int = int(total_orders)
        average_order_value = (
            total_revenue_decimal / Decimal(total_orders_int)
            if total_orders_int > 0
            else Decimal('0')
        )
        return FinancialSummary(
            total_revenue=total_revenue_decimal,
            total_lines=int(total_lines),
            total_orders=total_orders_int,
            average_order_value=average_order_value,
        )

    def top_customers_by_revenue(self, limit: int) -> list[TopCustomerRevenue]:
        if limit <= 0:
            return []
        stmt = (
            select(
                VentaLinea.cliente_dynamics_id,
                Cliente.nombre,
                func.count(VentaLinea.id),
                func.coalesce(func.sum(VentaLinea.line_amount), 0),
            )
            .outerjoin(Cliente, VentaLinea.cliente_dynamics_id == Cliente.dynamics_id)
            .where(VentaLinea.cliente_dynamics_id.is_not(None))
            .group_by(VentaLinea.cliente_dynamics_id, Cliente.nombre)
            .order_by(func.sum(VentaLinea.line_amount).desc())
            .limit(limit)
        )
        rows = self._db.execute(stmt).all()
        return [
            TopCustomerRevenue(
                customer_account=row[0],
                customer_name=row[1],
                lines=int(row[2]),
                total_revenue=Decimal(str(row[3])),
            )
            for row in rows
        ]

    def top_products_by_revenue(self, limit: int) -> list[TopProductRevenue]:
        if limit <= 0:
            return []
        product_name = func.coalesce(VentaLinea.product_name, VentaLinea.product_number, 'Unknown')
        stmt = (
            select(
                VentaLinea.product_number,
                product_name,
                func.count(VentaLinea.id),
                func.coalesce(func.sum(VentaLinea.line_amount), 0),
            )
            .group_by(VentaLinea.product_number, product_name)
            .order_by(func.sum(VentaLinea.line_amount).desc())
            .limit(limit)
        )
        rows = self._db.execute(stmt).all()
        return [
            TopProductRevenue(
                product_number=row[0],
                product_name=row[1],
                lines=int(row[2]),
                total_revenue=Decimal(str(row[3])),
            )
            for row in rows
        ]

    def sales_by_line_status(self) -> list[SalesByLineStatus]:
        status_label = func.coalesce(VentaLinea.sales_order_line_status, 'Unknown')
        stmt = (
            select(status_label, func.count(VentaLinea.id), func.coalesce(func.sum(VentaLinea.line_amount), 0))
            .group_by(status_label)
            .order_by(func.sum(VentaLinea.line_amount).desc())
        )
        rows = self._db.execute(stmt).all()
        return [
            SalesByLineStatus(status=str(row[0]), count=int(row[1]), total_revenue=Decimal(str(row[2])))
            for row in rows
        ]

    def sales_by_product(self) -> list[ProductSales]:
        product_name = func.coalesce(VentaLinea.product_name, VentaLinea.product_number, 'Unknown')
        stmt = (
            select(
                VentaLinea.product_number,
                product_name,
                func.coalesce(func.sum(VentaLinea.line_amount), 0),
                func.coalesce(func.sum(VentaLinea.ordered_sales_quantity), 0),
            )
            .group_by(VentaLinea.product_number, product_name)
            .order_by(func.sum(VentaLinea.line_amount).desc())
        )
        rows = self._db.execute(stmt).all()
        return [
            ProductSales(
                product_number=row[0],
                product_name=row[1],
                total_revenue=Decimal(str(row[2])),
                total_quantity=Decimal(str(row[3])),
            )
            for row in rows
        ]

    def total_revenue(self) -> Decimal:
        value = self._db.scalar(select(func.coalesce(func.sum(VentaLinea.line_amount), 0))) or 0
        return Decimal(str(value))

    def count_lines(self) -> int:
        return self._db.scalar(select(func.count()).select_from(VentaLinea)) or 0
