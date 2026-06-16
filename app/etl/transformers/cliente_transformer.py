from typing import Any

def transform_cliente(record: dict[str, Any]) -> dict[str, Any] | None:
    dynamics_id = record.get('CustomerAccount')
    if not dynamics_id:
        return None
    nombre = record.get('OrganizationName') or record.get('NameAlias') or record.get('CustomerAccount')
    return {'dynamics_id': str(dynamics_id), 'nombre': str(nombre), 'email': record.get('PrimaryContactEmail'), 'telefono': record.get('PrimaryContactPhone')}

def transform_clientes(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    transformed = [transform_cliente(r) for r in records]
    return [r for r in transformed if r is not None]
