from collections.abc import Generator
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.session import get_db
from app.integrations.dynamics.factory import create_dynamics_client
from app.main import app
from app.models.base import Base
from app.models import cliente, venta, venta_linea

@pytest.fixture
def integration_db() -> Generator[Session, None, None]:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_dynamics_client() -> MagicMock:
    client = MagicMock()
    client.fetch_all_entity.side_effect = lambda entity, page_size=100, odata_filter=None: {
        'CustomersV3': [{'CustomerAccount': 'C001', 'OrganizationName': 'Cliente Uno SA', 'PrimaryContactEmail': 'uno@olnatura.com', 'PrimaryContactPhone': '555-0001'}, {'CustomerAccount': 'C002', 'NameAlias': 'Cliente Dos', 'PrimaryContactEmail': 'dos@olnatura.com'}],
        'SalesOrderHeadersV2': [{'SalesOrderNumber': 'SO-001', 'OrderingCustomerAccountNumber': 'C001', 'SalesOrderTotalAmount': 1500.5, 'RequestedShippingDate': '2025-06-01', 'SalesOrderStatus': 'Open'}, {'SalesOrderNumber': 'SO-002', 'OrderingCustomerAccountNumber': 'C002', 'SalesOrderTotalAmount': 3200.0, 'OrderCreationDateTime': '2025-06-10T10:00:00Z', 'SalesOrderStatus': 'Delivered'}],
        'D365SalesOrderLines': [{'SalesOrderNumber': 'SO-001', 'LineCreationSequenceNumber': 1, 'OrderingCustomerAccountNumber': 'C001', 'ProductNumber': 'P-100', 'ProductName': 'Producto Natural', 'OrderedSalesQuantity': 10, 'SalesPrice': 64821.858, 'LineAmount': 648218.58, 'SalesOrderLineStatus': 'Invoiced', 'CurrencyCode': 'MXN'}],
    }.get(entity, [])
    return client

@pytest.fixture
def integration_client(integration_db: Session, mock_dynamics_client: MagicMock) -> Generator[TestClient, None, None]:

    def override_get_db() -> Generator[Session, None, None]:
        yield integration_db
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[create_dynamics_client] = lambda: mock_dynamics_client
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
