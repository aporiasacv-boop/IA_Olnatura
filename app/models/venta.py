from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin

class Venta(Base, TimestampMixin):
    __tablename__ = 'ventas'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dynamics_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    cliente_dynamics_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sales_order_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    invoice_customer_account: Mapped[str | None] = mapped_column(String(50), nullable=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
