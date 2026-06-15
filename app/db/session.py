"""
Sesión y engine de SQLAlchemy 2.x para PostgreSQL.

Responsabilidad:
    - Crear el engine de conexión a PostgreSQL.
    - Exponer SessionFactory (fábrica de sesiones).
    - Proveer get_db() para inyección de dependencias en FastAPI.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Engine: punto central de conexión con PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DEBUG,
)

# Session Factory: genera una sesión ORM independiente por request
SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
    expire_on_commit=False,
)

# Alias retrocompatible con la estructura inicial del proyecto
SessionLocal = SessionFactory


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia FastAPI que provee una sesión de BD por request.

    Garantiza cierre de sesión al finalizar el ciclo de vida del request,
    evitando fugas de conexiones en el pool.
    """
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()


def ping_database(db: Session) -> bool:
    """
    Ejecuta SELECT 1 contra PostgreSQL para verificar conectividad.

    Returns:
        True si la consulta responde correctamente.
    """
    result = db.execute(text("SELECT 1")).scalar()
    return result == 1


def init_db() -> None:
    """
    Inicializa la base de datos creando tablas según los modelos definidos.

    En producción se recomienda usar migraciones (Alembic) en lugar de create_all.
    """
    from app.models import cliente, venta  # noqa: F401
    from app.models.base import Base

    Base.metadata.create_all(bind=engine)
