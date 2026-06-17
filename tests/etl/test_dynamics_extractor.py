from unittest.mock import MagicMock

from app.core.config import Settings
from app.etl.extractors.dynamics_extractor import DynamicsExtractor

def test_extract_entity_applies_date_filter_for_sales_orders() -> None:
    client = MagicMock()
    client.fetch_all_entity.return_value = [{'SalesOrderNumber': 'SO-001'}]
    settings = Settings(
        SYNC_START_DATE='2025-01-01',
        SYNC_END_DATE='2025-12-31',
    )
    extractor = DynamicsExtractor(client, app_settings=settings)
    records = extractor.extract_entity('SalesOrderHeadersV2')
    assert len(records) == 1
    client.fetch_all_entity.assert_called_once()
    call_kwargs = client.fetch_all_entity.call_args.kwargs
    assert 'OrderCreationDateTime' in call_kwargs['odata_filter']

def test_extract_entity_without_dates_has_no_filter() -> None:
    client = MagicMock()
    client.fetch_all_entity.return_value = [{'CustomerAccount': 'C001'}]
    settings = Settings(SYNC_START_DATE='', SYNC_END_DATE='')
    extractor = DynamicsExtractor(client, app_settings=settings)
    extractor.extract_entity('CustomersV3')
    call_kwargs = client.fetch_all_entity.call_args.kwargs
    assert call_kwargs['odata_filter'] is None
