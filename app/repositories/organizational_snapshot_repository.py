from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.models.organizational_snapshot import OrganizationalSnapshot

class OrganizationalSnapshotRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, snapshot: OrganizationalSnapshot) -> OrganizationalSnapshot:
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_latest(self) -> OrganizationalSnapshot | None:
        return self.db.scalars(
            select(OrganizationalSnapshot).order_by(desc(OrganizationalSnapshot.id)).limit(1)
        ).first()

    def get_previous(self) -> OrganizationalSnapshot | None:
        return self.db.scalars(
            select(OrganizationalSnapshot).order_by(desc(OrganizationalSnapshot.id)).offset(1).limit(1)
        ).first()

    def count(self) -> int:
        return len(self.db.scalars(select(OrganizationalSnapshot)).all())
