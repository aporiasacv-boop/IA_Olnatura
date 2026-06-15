"""
Repositorio de clientes con operaciones de upsert.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories.upsert import bulk_upsert


class ClienteRepository:
    """Persistencia de clientes sincronizados desde Dynamics 365."""

    def __init__(self, db: Session):
        self.db = db

    def upsert_many(self, records: list[dict[str, Any]]) -> int:
        """
        Inserta o actualiza clientes por dynamics_id.

        Args:
            records: Diccionarios con campos del modelo Cliente.

        Returns:
            Cantidad de registros procesados.
        """
        if not records:
            return 0

        now = datetime.now(timezone.utc)
        payload = [{**record, "synced_at": now, "updated_at": now} for record in records]
        count = bulk_upsert(
            self.db,
            Cliente.__table__,
            payload,
            index_elements=["dynamics_id"],
        )
        self.db.commit()
        return count

    def count(self) -> int:
        """Retorna el total de clientes almacenados."""
        from sqlalchemy import func, select

        return self.db.scalar(select(func.count()).select_from(Cliente)) or 0
