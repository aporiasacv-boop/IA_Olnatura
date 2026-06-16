from sqlalchemy.orm import Session
from app.db.session import ping_database

class DbHealthService:

    def __init__(self, db: Session):
        self.db = db

    def is_connected(self) -> bool:
        return ping_database(self.db)
