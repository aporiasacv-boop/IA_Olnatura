from decimal import Decimal
from datetime import date
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session
from app.domain.analytics import ClienteVentas, SalesByStatus, SalesSummary, TopCustomer, TotalVentasMes
from app.models.cliente import Cliente
from app.models.venta import Venta

class AnalyticsRepository:

    def __init__(self, db: Session):
        self._db = db

    def total_ventas_mes(self, year: int, month: int) -> TotalVentasMes:
        stmt = select(func.coalesce(func.sum(Venta.monto), 0), func.count(Venta.id)).where(Venta.fecha.is_not(None), extract('year', Venta.fecha) == year, extract('month', Venta.fecha) == month)
        total, cantidad = self._db.execute(stmt).one()
        return TotalVentasMes(year=year, month=month, total=Decimal(str(total)), cantidad_ventas=int(cantidad))

    def ventas_por_cliente(self) -> list[ClienteVentas]:
        stmt = select(Venta.cliente_dynamics_id, Cliente.nombre, func.coalesce(func.sum(Venta.monto), 0), func.count(Venta.id)).outerjoin(Cliente, Venta.cliente_dynamics_id == Cliente.dynamics_id).group_by(Venta.cliente_dynamics_id, Cliente.nombre).order_by(func.sum(Venta.monto).desc())
        rows = self._db.execute(stmt).all()
        return [ClienteVentas(cliente_dynamics_id=row[0], nombre=row[1], total_ventas=Decimal(str(row[2])), cantidad_ventas=int(row[3])) for row in rows]

    def count_clientes(self) -> int:
        return self._db.scalar(select(func.count()).select_from(Cliente)) or 0

    def top_clientes(self, limit: int) -> list[ClienteVentas]:
        if limit <= 0:
            return []
        stmt = select(Venta.cliente_dynamics_id, Cliente.nombre, func.coalesce(func.sum(Venta.monto), 0), func.count(Venta.id)).outerjoin(Cliente, Venta.cliente_dynamics_id == Cliente.dynamics_id).group_by(Venta.cliente_dynamics_id, Cliente.nombre).order_by(func.sum(Venta.monto).desc()).limit(limit)
        rows = self._db.execute(stmt).all()
        return [ClienteVentas(cliente_dynamics_id=row[0], nombre=row[1], total_ventas=Decimal(str(row[2])), cantidad_ventas=int(row[3])) for row in rows]

    def count_ventas(self) -> int:
        return self._db.scalar(select(func.count()).select_from(Venta)) or 0

    def sales_summary(self) -> SalesSummary:
        stmt = select(func.count(Venta.id), func.coalesce(func.sum(Venta.monto), 0), func.coalesce(func.avg(Venta.monto), 0))
        total_orders, total_amount, average_amount = self._db.execute(stmt).one()
        return SalesSummary(total_orders=int(total_orders), total_amount=Decimal(str(total_amount)), average_order_amount=Decimal(str(average_amount)))

    def sales_by_status(self) -> list[SalesByStatus]:
        status_label = func.coalesce(Venta.estado, 'Unknown')
        stmt = select(status_label, func.count(Venta.id)).group_by(status_label).order_by(func.count(Venta.id).desc())
        rows = self._db.execute(stmt).all()
        return [SalesByStatus(status=str(row[0]), count=int(row[1])) for row in rows]

    def top_customers(self, limit: int) -> list[TopCustomer]:
        if limit <= 0:
            return []
        stmt = select(Venta.cliente_dynamics_id, Cliente.nombre, func.count(Venta.id), func.coalesce(func.sum(Venta.monto), 0)).outerjoin(Cliente, Venta.cliente_dynamics_id == Cliente.dynamics_id).group_by(Venta.cliente_dynamics_id, Cliente.nombre).order_by(func.sum(Venta.monto).desc()).limit(limit)
        rows = self._db.execute(stmt).all()
        return [TopCustomer(customer_account=row[0], customer_name=row[1], orders=int(row[2]), total_amount=Decimal(str(row[3]))) for row in rows]

    def sales_date_range(self) -> tuple[date | None, date | None]:
        start_date, end_date = self._db.execute(select(func.min(Venta.fecha), func.max(Venta.fecha))).one()
        return start_date, end_date
