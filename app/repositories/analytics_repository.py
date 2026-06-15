"""
Repositorio de consultas analíticas empresariales.

Encapsula agregaciones SQL sobre ventas y clientes.
"""

from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.domain.analytics import ClienteVentas, TotalVentasMes
from app.models.cliente import Cliente
from app.models.venta import Venta


class AnalyticsRepository:
    """Implementación SQLAlchemy del repositorio analítico."""

    def __init__(self, db: Session):
        self._db = db

    def total_ventas_mes(self, year: int, month: int) -> TotalVentasMes:
        """
        Suma ventas cuya fecha cae en el año y mes indicados.

        Ventas sin fecha se excluyen del cálculo.
        """
        stmt = select(
            func.coalesce(func.sum(Venta.monto), 0),
            func.count(Venta.id),
        ).where(
            Venta.fecha.is_not(None),
            extract("year", Venta.fecha) == year,
            extract("month", Venta.fecha) == month,
        )

        total, cantidad = self._db.execute(stmt).one()
        return TotalVentasMes(
            year=year,
            month=month,
            total=Decimal(str(total)),
            cantidad_ventas=int(cantidad),
        )

    def ventas_por_cliente(self) -> list[ClienteVentas]:
        """Agrupa todas las ventas por cliente con join opcional al catálogo."""
        stmt = (
            select(
                Venta.cliente_dynamics_id,
                Cliente.nombre,
                func.coalesce(func.sum(Venta.monto), 0),
                func.count(Venta.id),
            )
            .outerjoin(Cliente, Venta.cliente_dynamics_id == Cliente.dynamics_id)
            .group_by(Venta.cliente_dynamics_id, Cliente.nombre)
            .order_by(func.sum(Venta.monto).desc())
        )

        rows = self._db.execute(stmt).all()
        return [
            ClienteVentas(
                cliente_dynamics_id=row[0],
                nombre=row[1],
                total_ventas=Decimal(str(row[2])),
                cantidad_ventas=int(row[3]),
            )
            for row in rows
        ]

    def count_clientes(self) -> int:
        """Retorna el total de clientes en la base de datos."""
        return self._db.scalar(select(func.count()).select_from(Cliente)) or 0

    def top_clientes(self, limit: int) -> list[ClienteVentas]:
        """Retorna los N clientes con mayor monto total de ventas."""
        if limit <= 0:
            return []

        stmt = (
            select(
                Venta.cliente_dynamics_id,
                Cliente.nombre,
                func.coalesce(func.sum(Venta.monto), 0),
                func.count(Venta.id),
            )
            .outerjoin(Cliente, Venta.cliente_dynamics_id == Cliente.dynamics_id)
            .group_by(Venta.cliente_dynamics_id, Cliente.nombre)
            .order_by(func.sum(Venta.monto).desc())
            .limit(limit)
        )

        rows = self._db.execute(stmt).all()
        return [
            ClienteVentas(
                cliente_dynamics_id=row[0],
                nombre=row[1],
                total_ventas=Decimal(str(row[2])),
                cantidad_ventas=int(row[3]),
            )
            for row in rows
        ]
