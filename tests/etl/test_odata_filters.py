from datetime import date

from app.etl.odata_filters import build_date_range_filter, build_entity_filter

def test_build_date_range_filter() -> None:
    filter_value = build_date_range_filter(
        'OrderCreationDateTime',
        date(2025, 1, 1),
        date(2025, 12, 31),
    )
    assert filter_value == (
        'OrderCreationDateTime ge 2025-01-01T00:00:00Z and '
        'OrderCreationDateTime le 2025-12-31T23:59:59Z'
    )

def test_build_entity_filter_for_sales_orders() -> None:
    filter_value = build_entity_filter(
        'SalesOrderHeadersV2',
        date(2025, 1, 1),
        date(2025, 12, 31),
    )
    assert filter_value is not None
    assert 'OrderCreationDateTime' in filter_value

def test_build_entity_filter_for_sales_lines() -> None:
    filter_value = build_entity_filter(
        'D365SalesOrderLines',
        date(2025, 1, 1),
        date(2025, 12, 31),
    )
    assert filter_value is not None
    assert 'ConfirmedShippingDate' in filter_value

def test_build_entity_filter_skips_customers() -> None:
    assert build_entity_filter('CustomersV3', date(2025, 1, 1), date(2025, 12, 31)) is None

def test_build_entity_filter_requires_both_dates() -> None:
    assert build_entity_filter('SalesOrderHeadersV2', None, date(2025, 12, 31)) is None
