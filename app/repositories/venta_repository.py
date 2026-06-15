"""
Repositorio de ventas con operaciones de upsert.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.venta import Venta
from app.repositories.upsert import bulk_upsert


class VentaRepository:
    """Persistencia de ventas sincronizadas desde Dynamics 365."""

    def __init__(self, db: Session):
        self.db = db

    def upsert_many(self, records: list[dict[str, Any]]) -> int:
        """
        Inserta o actualiza ventas por dynamics_id.

        Args:
            records: Diccionarios con campos del modelo Venta.

        Returns:
            Cantidad de registros procesados.
        """
        if not records:
            return 0

        now = datetime.now(timezone.utc)
        payload = [{**record, "synced_at": now, "updated_at": now} for record in records]
        count = bulk_upsert(
            self.db,
            Venta.__table__,
            payload,
            index_elements=["dynamics_id"],
        )
        self.db.commit()
        return count

    def count(self) -> int:
        """Retorna el total de ventas almacenadas."""
        from sqlalchemy import func, select

        return self.db.scalar(select(func.count()).select_from(Venta)) or 0
