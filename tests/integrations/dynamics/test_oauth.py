from unittest.mock import MagicMock
import httpx
import pytest
from app.integrations.dynamics.exceptions import DynamicsAuthError, DynamicsConnectionError
from app.integrations.dynamics.oauth import AzureADOAuthProvider, OAuthConfig

@pytest.fixture
def oauth_config() -> OAuthConfig:
    return OAuthConfig(tenant_id='tenant-id', client_id='client-id', client_secret='client-secret', scope='https://example.operations.dynamics.com/.default', token_url='https://login.microsoftonline.com/tenant-id/oauth2/v2.0/token', timeout=5.0)

def test_get_access_token_returns_bearer_token(oauth_config: OAuthConfig) -> None:
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 200
    http_response.json.return_value = {'access_token': 'test-token', 'expires_in': 3600}
    http_client.post.return_value = http_response
    provider = AzureADOAuthProvider(oauth_config, http_client=http_client)
    token = provider.get_access_token()
    assert token == 'test-token'
    http_client.post.assert_called_once()

def test_get_access_token_raises_auth_error_on_invalid_response(oauth_config: OAuthConfig) -> None:
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 401
    http_response.text = 'Unauthorized'
    http_client.post.return_value = http_response
    provider = AzureADOAuthProvider(oauth_config, http_client=http_client)
    with pytest.raises(DynamicsAuthError, match='Error OAuth 401'):
        provider.get_access_token()

def test_get_access_token_raises_connection_error_on_network_failure(oauth_config: OAuthConfig) -> None:
    http_client = MagicMock()
    http_client.post.side_effect = httpx.ConnectError('Connection refused')
    provider = AzureADOAuthProvider(oauth_config, http_client=http_client)
    with pytest.raises(DynamicsConnectionError, match='No se pudo conectar'):
        provider.get_access_token()

def test_get_access_token_uses_cache_on_second_call(oauth_config: OAuthConfig) -> None:
    http_client = MagicMock()
    http_response = MagicMock()
    http_response.status_code = 200
    http_response.json.return_value = {'access_token': 'cached-token', 'expires_in': 3600}
    http_client.post.return_value = http_response
    provider = AzureADOAuthProvider(oauth_config, http_client=http_client)
    first = provider.get_access_token()
    second = provider.get_access_token()
    assert first == second == 'cached-token'
    assert http_client.post.call_count == 1
