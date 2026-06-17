from unittest.mock import MagicMock

from app.integrations.dynamics.odata_client import DynamicsODataClient, ODataClientConfig

def test_fetch_all_entity_applies_odata_filter() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'value': [{'SalesOrderNumber': 'SO-001'}]}
    http_client.get.return_value = response
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    records = client.fetch_all_entity(
        'SalesOrderHeadersV2',
        page_size=100,
        odata_filter='OrderCreationDateTime ge 2025-01-01T00:00:00Z',
    )
    assert len(records) == 1
    http_client.get.assert_called_once()
    call_kwargs = http_client.get.call_args.kwargs
    assert call_kwargs['params']['$filter'] == 'OrderCreationDateTime ge 2025-01-01T00:00:00Z'
    assert '$top' not in call_kwargs['params']
    assert call_kwargs['headers']['Prefer'] == 'odata.maxpagesize=100'

def test_fetch_all_entity_sends_prefer_header_instead_of_top() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'value': [{'CustomerAccount': 'C001'}]}
    http_client.get.return_value = response
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    client.fetch_all_entity('CustomersV3', page_size=50)
    call_kwargs = http_client.get.call_args.kwargs
    assert call_kwargs['headers']['Prefer'] == 'odata.maxpagesize=50'
    assert call_kwargs.get('params') is None or '$top' not in (call_kwargs.get('params') or {})

def test_fetch_all_entity_follows_next_link() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    first_response = MagicMock()
    first_response.status_code = 200
    first_response.json.return_value = {
        'value': [{'CustomerAccount': 'C001'}],
        '@odata.nextLink': 'https://example.operations.dynamics.com/data/CustomersV3?$skiptoken=abc',
    }
    second_response = MagicMock()
    second_response.status_code = 200
    second_response.json.return_value = {'value': [{'CustomerAccount': 'C002'}]}
    http_client.get.side_effect = [first_response, second_response]
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    records = client.fetch_all_entity('CustomersV3', page_size=10)
    assert len(records) == 2
    assert records[0]['CustomerAccount'] == 'C001'
    assert records[1]['CustomerAccount'] == 'C002'
    assert http_client.get.call_count == 2
    first_call = http_client.get.call_args_list[0].kwargs
    second_call = http_client.get.call_args_list[1].kwargs
    assert first_call['headers']['Prefer'] == 'odata.maxpagesize=10'
    assert 'Prefer' not in second_call['headers']

def test_fetch_all_entity_continues_with_skip_when_next_link_stops() -> None:
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = 'token'
    prefer_page = MagicMock()
    prefer_page.status_code = 200
    prefer_page.json.return_value = {
        'value': [{'SalesOrderNumber': f'SO-{i:03d}'} for i in range(100)],
        '@odata.nextLink': 'https://example.operations.dynamics.com/data/SalesOrderHeadersV2?$skip=100&$top=100',
    }
    next_link_page = MagicMock()
    next_link_page.status_code = 200
    next_link_page.json.return_value = {
        'value': [{'SalesOrderNumber': f'SO-{i:03d}'} for i in range(100, 200)],
    }
    skip_page = MagicMock()
    skip_page.status_code = 200
    skip_page.json.return_value = {
        'value': [{'SalesOrderNumber': 'SO-200'}],
    }
    http_client.get.side_effect = [prefer_page, next_link_page, skip_page]
    client = DynamicsODataClient(
        config=ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies'),
        oauth_provider=oauth,
        http_client=http_client,
    )
    records = client.fetch_all_entity('SalesOrderHeadersV2', page_size=100)
    assert len(records) == 201
    assert http_client.get.call_count == 3
    skip_call = http_client.get.call_args_list[2].kwargs
    assert skip_call['params']['$skip'] == 200
    assert skip_call['params']['$top'] == 100
