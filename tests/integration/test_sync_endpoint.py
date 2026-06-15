"""
Pruebas de integración del endpoint POST /sync.
"""

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.venta import Venta


def test_post_sync_endpoint(integration_client: TestClient, integration_db: Session) -> None:
    """Verifica sincronización manual vía POST /sync con BD real SQLite."""
    response = integration_client.post("/sync")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["errors"] == []
    assert data["clientes"]["extracted"] == 2
    assert data["clientes"]["upserted"] == 2
    assert data["ventas"]["extracted"] == 2
    assert data["ventas"]["upserted"] == 2

    assert integration_db.query(Cliente).count() == 2
    assert integration_db.query(Venta).count() == 2

    venta = integration_db.query(Venta).filter_by(dynamics_id="SO-002").one()
    assert venta.monto == Decimal("3200.00")
    assert venta.cliente_dynamics_id == "C002"
