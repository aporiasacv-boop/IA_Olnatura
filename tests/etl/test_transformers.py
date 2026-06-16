from decimal import Decimal
from app.etl.transformers.cliente_transformer import transform_clientes
from app.etl.transformers.venta_transformer import transform_ventas

def test_transform_clientes_maps_fields() -> None:
    records = [{'CustomerAccount': 'C001', 'OrganizationName': 'Olnatura SA', 'PrimaryContactEmail': 'info@olnatura.com'}, {'CustomerAccount': None}]
    result = transform_clientes(records)
    assert len(result) == 1
    assert result[0]['dynamics_id'] == 'C001'
    assert result[0]['nombre'] == 'Olnatura SA'

def test_transform_ventas_maps_fields() -> None:
    records = [{'SalesOrderNumber': 'SO-100', 'OrderingCustomerAccountNumber': 'C001', 'SalesOrderTotalAmount': 500.25, 'RequestedShippingDate': '2025-01-15', 'SalesOrderStatus': 'Open'}]
    result = transform_ventas(records)
    assert len(result) == 1
    assert result[0]['dynamics_id'] == 'SO-100'
    assert result[0]['monto'] == Decimal('500.25')
