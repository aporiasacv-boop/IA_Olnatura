from decimal import Decimal
from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.models import cliente, venta, venta_linea
from app.models.cliente import Cliente
from app.models.venta_linea import VentaLinea
from app.repositories.venta_linea_repository import VentaLineaRepository

@pytest.fixture
def venta_linea_db():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    yield session
    session.close()

def test_upsert_many_inserts_and_updates_without_duplicates(venta_linea_db) -> None:
    repo = VentaLineaRepository(venta_linea_db)
    records = [{
        'sales_order_number': 'SO-001',
        'line_creation_sequence_number': 1,
        'cliente_dynamics_id': 'C001',
        'product_number': 'P1',
        'product_name': 'Producto 1',
        'ordered_sales_quantity': Decimal('2'),
        'sales_price': Decimal('100'),
        'line_amount': Decimal('200'),
        'sales_order_line_status': 'Invoiced',
        'currency_code': 'MXN',
        'fecha': date(2025, 6, 1),
    }]
    inserted, updated = repo.upsert_many_with_metrics(records)
    assert inserted == 1
    assert updated == 0
    records[0]['line_amount'] = Decimal('250')
    inserted, updated = repo.upsert_many_with_metrics(records)
    assert inserted == 0
    assert updated == 1
    assert venta_linea_db.query(VentaLinea).count() == 1
    assert venta_linea_db.query(VentaLinea).one().line_amount == Decimal('250')
