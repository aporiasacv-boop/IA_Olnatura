from collections.abc import Generator
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models import cliente, venta
from app.models.cliente import Cliente
from app.models.venta import Venta

@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_db_session() -> MagicMock:
    session = MagicMock(spec=Session)
    session.execute.return_value.scalar.return_value = 1
    return session

@pytest.fixture
def client_with_db(mock_db_session: MagicMock) -> Generator[TestClient, None, None]:

    def override_get_db_session() -> Generator[MagicMock, None, None]:
        yield mock_db_session
    app.dependency_overrides[get_db] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def analytics_db() -> Generator[Session, None, None]:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    session.add_all([Cliente(dynamics_id='C001', nombre='Alpha Corp'), Cliente(dynamics_id='C002', nombre='Beta SA'), Cliente(dynamics_id='C003', nombre='Gamma Ltd')])
    session.add_all([Venta(dynamics_id='SO-001', cliente_dynamics_id='C001', monto=Decimal('1000.00'), fecha=date(2025, 6, 1), estado='Open'), Venta(dynamics_id='SO-002', cliente_dynamics_id='C001', monto=Decimal('500.00'), fecha=date(2025, 6, 15), estado='Delivered'), Venta(dynamics_id='SO-003', cliente_dynamics_id='C002', monto=Decimal('3000.00'), fecha=date(2025, 6, 10), estado='Open'), Venta(dynamics_id='SO-004', cliente_dynamics_id='C003', monto=Decimal('200.00'), fecha=date(2025, 5, 20), estado='Closed'), Venta(dynamics_id='SO-005', cliente_dynamics_id='C002', monto=Decimal('800.00'), fecha=None, estado='Draft')])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
