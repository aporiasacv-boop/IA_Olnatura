"""
Sesión y engine de SQLAlchemy.

Responsabilidad:
    - Crear el engine de conexión a PostgreSQL.
    - Proveer SessionLocal para inyección de dependencias.
    - Inicializar metadatos de modelos (create_all en desarrollo).
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Engine: punto central de conexión con la base de datos
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DEBUG,  # Log de SQL en modo debug
)

# Fábrica de sesiones: cada request obtiene su propia sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia FastAPI que provee una sesión de BD por request.

    Garantiza cierre de sesión al finalizar el ciclo de vida del request,
    evitando fugas de conexiones.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando tablas según los modelos definidos.

    En producción se recomienda usar migraciones (Alembic) en lugar de create_all.
    """
    # Importación diferida para evitar importaciones circulares
    from app.models.base import Base

    Base.metadata.create_all(bind=engine)
