from datetime import date, datetime
from decimal import Decimal
from typing import Any

def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
    return None

def _parse_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal('0')
    return Decimal(str(value))

def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)

def transform_venta_linea(record: dict[str, Any]) -> dict[str, Any] | None:
    sales_order_number = record.get('SalesOrderNumber')
    line_sequence = _parse_int(record.get('LineCreationSequenceNumber'))
    if not sales_order_number or line_sequence is None:
        return None
    cliente_id = record.get('OrderingCustomerAccountNumber') or record.get('InvoiceCustomerAccountNumber')
    fecha = _parse_date(
        record.get('RequestedReceiptDate')
        or record.get('ConfirmedShippingDate')
        or record.get('RequestedShippingDate')
        or record.get('ShippingDateRequested')
    )
    return {
        'sales_order_number': str(sales_order_number),
        'line_creation_sequence_number': line_sequence,
        'cliente_dynamics_id': str(cliente_id) if cliente_id else None,
        'product_number': str(record['ProductNumber']) if record.get('ProductNumber') else None,
        'product_name': record.get('ProductName') or record.get('LineDescription'),
        'ordered_sales_quantity': _parse_decimal(record.get('OrderedSalesQuantity')),
        'sales_price': _parse_decimal(record.get('SalesPrice')),
        'line_amount': _parse_decimal(record.get('LineAmount')),
        'sales_order_line_status': record.get('SalesOrderLineStatus'),
        'currency_code': record.get('CurrencyCode'),
        'fecha': fecha,
    }

def transform_venta_lineas(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    transformed = [transform_venta_linea(record) for record in records]
    return [item for item in transformed if item is not None]
