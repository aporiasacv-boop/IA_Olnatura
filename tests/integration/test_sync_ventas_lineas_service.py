from decimal import Decimal
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.models.venta import Venta
from app.models.venta_linea import VentaLinea
from app.services.sync_service import SyncService

def test_sync_ventas_lineas_pipeline(integration_db: Session, mock_dynamics_client: MagicMock) -> None:
    integration_db.add(Venta(dynamics_id='SO-001', cliente_dynamics_id='C001', monto=Decimal('0'), estado='Open'))
    integration_db.commit()
    mock_dynamics_client.fetch_all_entity.side_effect = lambda entity, page_size=100, odata_filter=None: {
        'D365SalesOrderLines': [{
            'SalesOrderNumber': 'SO-001',
            'LineCreationSequenceNumber': 1,
            'ProductNumber': 'P-100',
            'ProductName': 'Producto Natural',
            'OrderedSalesQuantity': 10,
            'SalesPrice': 64821.858,
            'LineAmount': 648218.58,
            'SalesOrderLineStatus': 'Invoiced',
            'CurrencyCode': 'MXN',
        }],
    }.get(entity, [])
    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    result = service.run_ventas_lineas()
    assert result.errors == []
    assert result.entity == 'D365SalesOrderLines'
    assert result.read == 1
    assert result.inserted == 1
    line = integration_db.query(VentaLinea).one()
    assert line.sales_order_number == 'SO-001'
    assert line.cliente_dynamics_id == 'C001'
    assert line.line_amount == Decimal('648218.58')

def test_sync_ventas_lineas_enriches_customer_from_ventas(integration_db: Session, mock_dynamics_client: MagicMock) -> None:
    integration_db.add(Venta(dynamics_id='390003546', cliente_dynamics_id='C0028', monto=Decimal('0'), estado='Invoiced'))
    integration_db.commit()
    mock_dynamics_client.fetch_all_entity.side_effect = lambda entity, page_size=100, odata_filter=None: {
        'D365SalesOrderLines': [{
            'SalesOrderNumber': '390003546',
            'LineCreationSequenceNumber': 1,
            'ProductNumber': 'P-200',
            'LineAmount': 1000.0,
        }],
    }.get(entity, [])
    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    result = service.run_ventas_lineas()
    assert result.inserted == 1
    line = integration_db.query(VentaLinea).one()
    assert line.cliente_dynamics_id == 'C0028'
