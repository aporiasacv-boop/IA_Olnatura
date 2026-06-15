"""
Servicio de verificación de conectividad con PostgreSQL.
"""

from sqlalchemy.orm import Session

from app.db.session import ping_database


class DbHealthService:
    """Encapsula la lógica de health check de base de datos."""

    def __init__(self, db: Session):
        self.db = db

    def is_connected(self) -> bool:
        """Verifica que PostgreSQL responda a SELECT 1."""
        return ping_database(self.db)
