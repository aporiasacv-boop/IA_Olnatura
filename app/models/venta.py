"""
Modelo ORM para ventas sincronizadas desde Dynamics 365 F&O.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Venta(Base, TimestampMixin):
    """Venta extraída de la entidad OData SalesOrderHeadersV2."""

    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dynamics_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    cliente_dynamics_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str | None] = mapped_column(String(100), nullable=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
