"""
Transformador de ventas Dynamics 365 → modelo local.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any


def _parse_date(value: Any) -> date | None:
    """Convierte fechas OData (str/datetime) a date."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    return None


def _parse_decimal(value: Any) -> Decimal:
    """Convierte montos OData a Decimal."""
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def transform_venta(record: dict[str, Any]) -> dict[str, Any] | None:
    """
    Mapea un registro SalesOrderHeadersV2 al esquema de la tabla ventas.

    Returns:
        Diccionario transformado o None si el registro es inválido.
    """
    dynamics_id = record.get("SalesOrderNumber")
    cliente_id = record.get("OrderingCustomerAccountNumber")
    if not dynamics_id or not cliente_id:
        return None

    fecha = _parse_date(
        record.get("RequestedShippingDate") or record.get("OrderCreationDateTime")
    )

    return {
        "dynamics_id": str(dynamics_id),
        "cliente_dynamics_id": str(cliente_id),
        "monto": _parse_decimal(record.get("SalesOrderTotalAmount")),
        "fecha": fecha,
        "estado": record.get("SalesOrderStatus"),
    }


def transform_ventas(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transforma una lista de registros OData de ventas."""
    transformed = [transform_venta(r) for r in records]
    return [r for r in transformed if r is not None]
