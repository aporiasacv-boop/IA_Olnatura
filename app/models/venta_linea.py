from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin

class VentaLinea(Base, TimestampMixin):
    __tablename__ = 'venta_lineas'
    __table_args__ = (
        UniqueConstraint('sales_order_number', 'line_creation_sequence_number', name='uq_venta_lineas_order_line'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sales_order_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    line_creation_sequence_number: Mapped[int] = mapped_column(nullable=False)
    cliente_dynamics_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    product_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ordered_sales_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    sales_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    sales_order_line_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
