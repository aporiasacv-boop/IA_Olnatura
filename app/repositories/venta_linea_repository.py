from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.venta_linea import VentaLinea
from app.repositories.upsert import bulk_upsert

class VentaLineaRepository:

    def __init__(self, db: Session):
        self.db = db

    def upsert_many(self, records: list[dict[str, Any]]) -> int:
        inserted, updated = self.upsert_many_with_metrics(records)
        return inserted + updated

    def upsert_many_with_metrics(self, records: list[dict[str, Any]]) -> tuple[int, int]:
        if not records:
            return 0, 0
        keys = [(record['sales_order_number'], record['line_creation_sequence_number']) for record in records]
        existing = {
            (row.sales_order_number, row.line_creation_sequence_number)
            for row in self.db.scalars(
                select(VentaLinea).where(
                    VentaLinea.sales_order_number.in_({key[0] for key in keys}),
                )
            )
            if keys
        }
        inserted = sum(1 for key in keys if key not in existing)
        updated = len(records) - inserted
        now = datetime.now(timezone.utc)
        payload = [{**record, 'synced_at': now, 'updated_at': now} for record in records]
        bulk_upsert(
            self.db,
            VentaLinea.__table__,
            payload,
            index_elements=['sales_order_number', 'line_creation_sequence_number'],
        )
        self.db.commit()
        return inserted, updated

    def count(self) -> int:
        from sqlalchemy import func
        return self.db.scalar(select(func.count()).select_from(VentaLinea)) or 0
