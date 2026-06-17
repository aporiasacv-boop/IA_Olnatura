from unittest.mock import MagicMock

from app.integrations.dynamics.odata_client import DynamicsODataClient, ODataClientConfig

def test_count_entity_parses_plain_text_response() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    response = MagicMock()
    response.status_code = 200
    response.text = '250'
    http_client.get.return_value = response
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    assert client.count_entity('CustomersV3') == 250

def test_count_entity_strips_utf8_bom() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    response = MagicMock()
    response.status_code = 200
    response.text = '\ufeff163'
    http_client.get.return_value = response
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    assert client.count_entity('CustomersV3') == 163

def test_paginate_entity_stats_tracks_pages_and_next_links() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    first = MagicMock()
    first.status_code = 200
    first.json.return_value = {
        'value': [{'CustomerAccount': f'C{i:03d}'} for i in range(100)],
        '@odata.nextLink': 'https://example.operations.dynamics.com/data/CustomersV3?$skiptoken=abc',
    }
    second = MagicMock()
    second.status_code = 200
    second.json.return_value = {'value': [{'CustomerAccount': 'C100'}]}
    http_client.get.side_effect = [first, second]
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    stats = client.paginate_entity_stats('CustomersV3', page_size=100)
    assert stats.total_records == 101
    assert stats.pages_traversed == 2
    assert stats.next_links_found == 1

def test_validate_filter_returns_false_on_odata_error() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    response = MagicMock()
    response.status_code = 400
    response.text = 'Invalid field'
    http_client.get.return_value = response
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    valid, error = client.validate_filter('SalesOrderHeadersV2', 'BadField ge 2025-01-01T00:00:00Z')
    assert valid is False
    assert error is not None
