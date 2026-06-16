from decimal import Decimal
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.integrations.dynamics.exceptions import DynamicsODataError
from app.models.venta import Venta
from app.services.sync_service import SyncService

def test_sync_ventas_pipeline(integration_db: Session, mock_dynamics_client: MagicMock) -> None:
    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    result = service.run_ventas()
    assert result.errors == []
    assert result.entity == 'D365SalesOrderHeaders'
    assert result.read == 2
    assert result.inserted == 2
    assert result.updated == 0
    ventas = integration_db.query(Venta).all()
    assert len(ventas) == 2
    assert ventas[0].dynamics_id == 'SO-001'
    assert ventas[0].monto == Decimal('1500.50')
    assert ventas[0].estado == 'Open'

def test_sync_ventas_upsert_updates_existing(integration_db: Session, mock_dynamics_client: MagicMock) -> None:
    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    service.run_ventas()
    mock_dynamics_client.fetch_all_entity.side_effect = lambda entity, page_size=100, max_records=None: [{'SalesOrderNumber': 'SO-001', 'OrderingCustomerAccountNumber': 'C001', 'SalesOrderName': 'Pedido actualizado', 'SalesOrderStatus': 'Invoiced', 'CurrencyCode': 'MXN', 'InvoiceCustomerAccountNumber': 'C001', 'SalesOrderTotalAmount': 9999.99}]
    result = service.run_ventas()
    assert result.inserted == 0
    assert result.updated == 1
    assert integration_db.query(Venta).count() == 2
    updated = integration_db.query(Venta).filter_by(dynamics_id='SO-001').one()
    assert updated.sales_order_name == 'Pedido actualizado'
    assert updated.monto == Decimal('9999.99')
    assert updated.currency_code == 'MXN'

def test_sync_ventas_handles_dynamics_error(integration_db: Session, mock_dynamics_client: MagicMock) -> None:
    mock_dynamics_client.fetch_all_entity.side_effect = DynamicsODataError('Error OData 500', status_code=500)
    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    result = service.run_ventas()
    assert len(result.errors) == 1
    assert result.read == 0
    assert integration_db.query(Venta).count() == 0
