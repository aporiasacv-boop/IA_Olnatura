from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings
engine = create_engine(settings.DATABASE_URL, pool_size=settings.DB_POOL_SIZE, max_overflow=settings.DB_MAX_OVERFLOW, pool_pre_ping=settings.DB_POOL_PRE_PING, echo=settings.DEBUG)
SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session, expire_on_commit=False)
SessionLocal = SessionFactory

def get_db() -> Generator[Session, None, None]:
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()

def ping_database(db: Session) -> bool:
    result = db.execute(text('SELECT 1')).scalar()
    return result == 1

def init_db() -> None:
    from app.models import cliente, venta
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
