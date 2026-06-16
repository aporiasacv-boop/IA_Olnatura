from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.venta import Venta
from app.repositories.upsert import bulk_upsert

class VentaRepository:

    def __init__(self, db: Session):
        self.db = db

    def upsert_many(self, records: list[dict[str, Any]]) -> int:
        inserted, updated = self.upsert_many_with_metrics(records)
        return inserted + updated

    def upsert_many_with_metrics(self, records: list[dict[str, Any]]) -> tuple[int, int]:
        if not records:
            return 0, 0
        dynamics_ids = [record['dynamics_id'] for record in records]
        existing = set(self.db.scalars(select(Venta.dynamics_id).where(Venta.dynamics_id.in_(dynamics_ids))).all())
        inserted = sum(1 for record in records if record['dynamics_id'] not in existing)
        updated = len(records) - inserted
        now = datetime.now(timezone.utc)
        payload = [{**record, 'synced_at': now, 'updated_at': now} for record in records]
        bulk_upsert(self.db, Venta.__table__, payload, index_elements=['dynamics_id'])
        self.db.commit()
        return inserted, updated

    def count(self) -> int:
        from sqlalchemy import func
        return self.db.scalar(select(func.count()).select_from(Venta)) or 0
