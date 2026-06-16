from unittest.mock import MagicMock
import httpx
import pytest
from app.integrations.dynamics.exceptions import DynamicsConnectionError, DynamicsODataError
from app.integrations.dynamics.odata_client import DynamicsODataClient, ODataClientConfig

@pytest.fixture
def odata_config() -> ODataClientConfig:
    return ODataClientConfig(base_url='https://example.operations.dynamics.com/data', health_entity='Companies', timeout=5.0)

@pytest.fixture
def oauth_provider() -> MagicMock:
    provider = MagicMock()
    provider.get_access_token.return_value = 'test-token'
    return provider

def test_query_entity_returns_odata_response(odata_config: ODataClientConfig, oauth_provider: MagicMock) -> None:
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 200
    http_response.json.return_value = {'value': [{'CompanyId': 'OLN'}]}
    http_client.get.return_value = http_response
    client = DynamicsODataClient(config=odata_config, oauth_provider=oauth_provider, http_client=http_client)
    result = client.query_entity('Companies', top=1)
    assert result == {'value': [{'CompanyId': 'OLN'}]}
    http_client.get.assert_called_once_with('https://example.operations.dynamics.com/data/Companies', headers={'Authorization': 'Bearer test-token', 'Accept': 'application/json'}, params={'$top': 1})

def test_ping_delegates_to_health_entity(odata_config: ODataClientConfig, oauth_provider: MagicMock) -> None:
    client = DynamicsODataClient(config=odata_config, oauth_provider=oauth_provider, http_client=MagicMock())
    client.query_entity = MagicMock(return_value={'value': []})
    client.ping()
    client.query_entity.assert_called_once_with('Companies', top=1)

def test_query_entity_raises_odata_error_on_http_failure(odata_config: ODataClientConfig, oauth_provider: MagicMock) -> None:
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 500
    http_response.text = 'Internal Server Error'
    http_client.get.return_value = http_response
    client = DynamicsODataClient(config=odata_config, oauth_provider=oauth_provider, http_client=http_client)
    with pytest.raises(DynamicsODataError, match='Error OData 500'):
        client.query_entity('Companies')

def test_query_entity_raises_connection_error_on_network_failure(odata_config: ODataClientConfig, oauth_provider: MagicMock) -> None:
    http_client = MagicMock()
    http_client.get.side_effect = httpx.TimeoutException('Timeout')
    client = DynamicsODataClient(config=odata_config, oauth_provider=oauth_provider, http_client=http_client)
    with pytest.raises(DynamicsConnectionError, match='No se pudo conectar'):
        client.query_entity('Companies')

def test_query_entity_raises_odata_error_when_value_missing(odata_config: ODataClientConfig, oauth_provider: MagicMock) -> None:
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 200
    http_response.json.return_value = {'error': 'invalid'}
    http_client.get.return_value = http_response
    client = DynamicsODataClient(config=odata_config, oauth_provider=oauth_provider, http_client=http_client)
    with pytest.raises(DynamicsODataError, match="no contiene el campo 'value'"):
        client.query_entity('Companies')
