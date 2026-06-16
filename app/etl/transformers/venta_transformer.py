from datetime import date, datetime
from decimal import Decimal
from typing import Any

def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and (not isinstance(value, datetime)):
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

def transform_venta(record: dict[str, Any]) -> dict[str, Any] | None:
    dynamics_id = record.get('SalesOrderNumber')
    cliente_id = record.get('OrderingCustomerAccountNumber')
    if not dynamics_id or not cliente_id:
        return None
    fecha = _parse_date(record.get('RequestedShippingDate') or record.get('OrderCreationDateTime'))
    return {
        'dynamics_id': str(dynamics_id),
        'cliente_dynamics_id': str(cliente_id),
        'monto': _parse_decimal(record.get('SalesOrderTotalAmount')),
        'fecha': fecha,
        'estado': record.get('SalesOrderStatus'),
        'sales_order_name': record.get('SalesOrderName'),
        'currency_code': record.get('CurrencyCode'),
        'invoice_customer_account': record.get('InvoiceCustomerAccountNumber'),
    }

def transform_ventas(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    transformed = [transform_venta(r) for r in records]
    return [r for r in transformed if r is not None]
