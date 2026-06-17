import json
from datetime import date
from decimal import Decimal
from typing import Any
from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin

class OrganizationalSnapshot(Base, TimestampMixin):
    __tablename__ = 'organizational_snapshots'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_customers: Mapped[int] = mapped_column(nullable=False, default=0)
    total_orders: Mapped[int] = mapped_column(nullable=False, default=0)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    top_customer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    top_customer_share: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    top_product: Mapped[str | None] = mapped_column(String(255), nullable=True)
    top_product_share: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    executive_insights_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'snapshot_date': self.snapshot_date.isoformat(),
            'total_customers': self.total_customers,
            'total_orders': self.total_orders,
            'total_revenue': format(self.total_revenue, '.2f'),
            'top_customer': self.top_customer,
            'top_customer_share': float(self.top_customer_share),
            'top_product': self.top_product,
            'top_product_share': float(self.top_product_share),
            'executive_insights': json.loads(self.executive_insights_json or '{}'),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
