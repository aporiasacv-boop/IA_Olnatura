import time
from dataclasses import dataclass
import httpx
from app.integrations.dynamics.exceptions import DynamicsAuthError, DynamicsConnectionError

@dataclass(frozen=True)
class OAuthConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    scope: str
    token_url: str
    timeout: float = 30.0

class AzureADOAuthProvider:

    def __init__(self, config: OAuthConfig, http_client: httpx.Client | None=None):
        self._config = config
        self._http_client = http_client or httpx.Client(timeout=config.timeout)
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    def get_access_token(self) -> str:
        if self._access_token and time.monotonic() < self._token_expires_at:
            return self._access_token
        self._access_token = None
        token = self._request_token()
        return token

    def _request_token(self) -> str:
        payload = {'grant_type': 'client_credentials', 'client_id': self._config.client_id, 'client_secret': self._config.client_secret, 'scope': self._config.scope}
        try:
            response = self._http_client.post(self._config.token_url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        except httpx.RequestError as exc:
            raise DynamicsConnectionError(f'No se pudo conectar al servidor OAuth: {exc}') from exc
        if response.status_code != 200:
            raise DynamicsAuthError(f'Error OAuth {response.status_code}: {response.text}')
        data = response.json()
        access_token = data.get('access_token')
        if not access_token:
            raise DynamicsAuthError('La respuesta OAuth no incluye access_token')
        expires_in = int(data.get('expires_in', 3600))
        self._token_expires_at = time.monotonic() + max(expires_in - 60, 0)
        self._access_token = access_token
        return access_token
