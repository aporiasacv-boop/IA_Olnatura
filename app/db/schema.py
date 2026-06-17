from sqlalchemy.engine import Engine
from app.models.base import Base

def ensure_database_schema(engine: Engine) -> None:
    from app.models import cliente, organizational_snapshot, user, venta, venta_linea
    Base.metadata.create_all(bind=engine)
