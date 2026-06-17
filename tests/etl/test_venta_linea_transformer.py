from decimal import Decimal
import pytest
from app.etl.transformers.venta_linea_transformer import transform_venta_lineas

def test_transform_venta_lineas_maps_fields() -> None:
    records = [{
        'SalesOrderNumber': '390003546',
        'LineCreationSequenceNumber': 1,
        'OrderingCustomerAccountNumber': 'C0005',
        'ProductNumber': 'P-100',
        'ProductName': 'Producto Natural',
        'OrderedSalesQuantity': 10,
        'SalesPrice': 64821.858,
        'LineAmount': 648218.58,
        'SalesOrderLineStatus': 'Invoiced',
        'CurrencyCode': 'MXN',
        'RequestedReceiptDate': '2020-06-15',
    }]
    result = transform_venta_lineas(records)
    assert len(result) == 1
    assert result[0]['sales_order_number'] == '390003546'
    assert result[0]['line_creation_sequence_number'] == 1
    assert result[0]['cliente_dynamics_id'] == 'C0005'
    assert result[0]['line_amount'] == Decimal('648218.58')

def test_transform_venta_lineas_without_customer_account() -> None:
    records = [{
        'SalesOrderNumber': '390003546',
        'LineCreationSequenceNumber': 2,
        'ProductNumber': 'P-200',
        'LineAmount': 100.0,
    }]
    result = transform_venta_lineas(records)
    assert len(result) == 1
    assert result[0]['cliente_dynamics_id'] is None

def test_transform_venta_lineas_skips_invalid_records() -> None:
    records = [{'SalesOrderNumber': 'SO-1'}, {'LineCreationSequenceNumber': 1}]
    assert transform_venta_lineas(records) == []
