from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.venta_linea import VentaLinea

def test_post_sync_ventas_lineas_endpoint(integration_client: TestClient, integration_db: Session) -> None:
    response = integration_client.post('/sync/ventas-lineas')
    assert response.status_code == 200
    data = response.json()
    assert data['entity'] == 'D365SalesOrderLines'
    assert data['errors'] == []
    assert data['read'] == 1
    assert data['inserted'] == 1
    line = integration_db.query(VentaLinea).one()
    assert line.line_amount == Decimal('648218.58')
