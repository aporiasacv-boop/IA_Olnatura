"""
Dependencias compartidas de la capa API.

Centraliza inyección de dependencias FastAPI reutilizables
en múltiples endpoints (sesión BD, servicios, autenticación futura).
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db


def get_db_session() -> Generator[Session, None, None]:
    """
    Alias explícito de get_db para la capa API.

    Permite extender o reemplazar la dependencia sin modificar endpoints.
    """
    yield from get_db()
