"""
Pruebas de integración del pipeline ETL SyncService.
"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.integrations.dynamics.exceptions import DynamicsODataError
from app.models.cliente import Cliente
from app.models.venta import Venta
from app.services.sync_service import SyncService


def test_sync_service_full_pipeline(
    integration_db: Session,
    mock_dynamics_client: MagicMock,
) -> None:
    """Verifica flujo ETL completo: extract → transform → upsert."""
    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    result = service.run()

    assert result.status == "completed"
    assert result.errors == []
    assert result.clientes.extracted == 2
    assert result.clientes.upserted == 2
    assert result.ventas.extracted == 2
    assert result.ventas.upserted == 2

    clientes = integration_db.query(Cliente).all()
    assert len(clientes) == 2
    assert clientes[0].dynamics_id == "C001"
    assert clientes[0].nombre == "Cliente Uno SA"

    ventas = integration_db.query(Venta).all()
    assert len(ventas) == 2
    assert ventas[0].dynamics_id == "SO-001"
    assert ventas[0].monto == Decimal("1500.50")


def test_sync_service_upsert_updates_existing_records(
    integration_db: Session,
    mock_dynamics_client: MagicMock,
) -> None:
    """Verifica que un segundo sync actualiza registros existentes (upsert)."""
    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    service.run()

    mock_dynamics_client.fetch_all_entity.side_effect = lambda entity, page_size=100: {
        "CustomersV3": [
            {
                "CustomerAccount": "C001",
                "OrganizationName": "Cliente Uno Actualizado",
                "PrimaryContactEmail": "nuevo@olnatura.com",
            },
        ],
        "SalesOrderHeadersV2": [
            {
                "SalesOrderNumber": "SO-001",
                "OrderingCustomerAccountNumber": "C001",
                "SalesOrderTotalAmount": 9999.99,
                "SalesOrderStatus": "Invoiced",
            },
        ],
    }.get(entity, [])

    result = service.run()

    assert result.status == "completed"
    assert integration_db.query(Cliente).count() == 2
    assert integration_db.query(Venta).count() == 2

    updated = integration_db.query(Cliente).filter_by(dynamics_id="C001").one()
    assert updated.nombre == "Cliente Uno Actualizado"
    assert updated.email == "nuevo@olnatura.com"

    updated_venta = integration_db.query(Venta).filter_by(dynamics_id="SO-001").one()
    assert updated_venta.monto == Decimal("9999.99")
    assert updated_venta.estado == "Invoiced"


def test_sync_service_handles_partial_failure(
    integration_db: Session,
    mock_dynamics_client: MagicMock,
) -> None:
    """Verifica que errores en ventas no impiden sincronizar clientes."""

    def side_effect(entity: str, page_size: int = 100) -> list:
        if entity == "SalesOrderHeadersV2":
            raise DynamicsODataError("Error OData 500", status_code=500)
        return [{"CustomerAccount": "C001", "OrganizationName": "Cliente Uno SA"}]

    mock_dynamics_client.fetch_all_entity.side_effect = side_effect

    service = SyncService(db=integration_db, dynamics_client=mock_dynamics_client)
    result = service.run()

    assert result.status == "completed_with_errors"
    assert len(result.errors) == 1
    assert "ventas" in result.errors[0].lower()
    assert result.clientes.upserted == 1
    assert result.ventas.upserted == 0
    assert integration_db.query(Cliente).count() == 1
    assert integration_db.query(Venta).count() == 0
