"""
Modelo base declarativo de SQLAlchemy.

Todas las entidades del sistema heredan de Base para compartir
metadatos y convenciones comunes (timestamps, etc.).
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Clase base declarativa para todos los modelos ORM.

    SQLAlchemy 2.0 usa DeclarativeBase en lugar del antiguo declarative_base().
    """

    pass


class TimestampMixin:
    """
    Mixin reutilizable con campos de auditoría temporal.

    Agregar a cualquier modelo que requiera created_at / updated_at.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
