from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.venta import Venta

def test_post_sync_ventas_endpoint(integration_client: TestClient, integration_db: Session) -> None:
    response = integration_client.post('/sync/ventas')
    assert response.status_code == 200
    data = response.json()
    assert data['entity'] == 'D365SalesOrderHeaders'
    assert data['errors'] == []
    assert data['read'] == 2
    assert data['inserted'] == 2
    assert data['updated'] == 0
    venta = integration_db.query(Venta).filter_by(dynamics_id='SO-002').one()
    assert venta.monto == Decimal('3200.00')
    assert venta.cliente_dynamics_id == 'C002'
