from datetime import date

ENTITY_DATE_FILTER_FIELDS: dict[str, str] = {
    'SalesOrderHeadersV2': 'OrderCreationDateTime',
    'D365SalesOrderLines': 'ConfirmedShippingDate',
}

def build_date_range_filter(field_name: str, start_date: date, end_date: date) -> str:
    start_value = f"{start_date.isoformat()}T00:00:00Z"
    end_value = f"{end_date.isoformat()}T23:59:59Z"
    return f"{field_name} ge {start_value} and {field_name} le {end_value}"

def build_entity_filter(entity_name: str, start_date: date | None, end_date: date | None) -> str | None:
    if start_date is None or end_date is None:
        return None
    field_name = ENTITY_DATE_FILTER_FIELDS.get(entity_name)
    if field_name is None:
        return None
    return build_date_range_filter(field_name, start_date, end_date)
