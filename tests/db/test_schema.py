from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool
from app.db.schema import ensure_database_schema

def test_ensure_database_schema_creates_ventas_table() -> None:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    ensure_database_schema(engine)
    table_names = set(inspect(engine).get_table_names())
    assert 'ventas' in table_names
    assert 'venta_lineas' in table_names
    assert 'clientes' in table_names
    assert 'users' in table_names
    with engine.connect() as connection:
        result = connection.execute(text('SELECT COUNT(*) FROM ventas')).scalar()
    assert result == 0
