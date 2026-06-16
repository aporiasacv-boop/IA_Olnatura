from dataclasses import dataclass
from typing import Any
import httpx
from app.integrations.dynamics.exceptions import DynamicsConnectionError, DynamicsODataError
from app.integrations.dynamics.protocols import OAuthTokenProvider

@dataclass(frozen=True)
class ODataClientConfig:
    base_url: str
    health_entity: str
    timeout: float = 30.0

class DynamicsODataClient:

    def __init__(self, config: ODataClientConfig, oauth_provider: OAuthTokenProvider, http_client: httpx.Client | None=None):
        self._config = config
        self._oauth_provider = oauth_provider
        self._http_client = http_client or httpx.Client(timeout=config.timeout)

    def ping(self) -> None:
        self.query_entity(self._config.health_entity, top=1)

    def query_entity(self, entity_name: str, top: int=1) -> dict[str, Any]:
        url = f"{self._config.base_url.rstrip('/')}/{entity_name}"
        return self._request_odata(url, params={'$top': top})

    def fetch_all_entity(self, entity_name: str, page_size: int=100) -> list[dict[str, Any]]:
        all_records: list[dict[str, Any]] = []
        next_url: str | None = f"{self._config.base_url.rstrip('/')}/{entity_name}"
        params: dict[str, int] | None = {'$top': page_size}
        while next_url:
            data = self._request_odata(next_url, params=params)
            all_records.extend(data.get('value', []))
            next_url = data.get('@odata.nextLink')
            params = None
        return all_records

    def _request_odata(self, url: str, params: dict[str, int] | None=None) -> dict[str, Any]:
        token = self._oauth_provider.get_access_token()
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        try:
            response = self._http_client.get(url, headers=headers, params=params)
        except httpx.RequestError as exc:
            raise DynamicsConnectionError(f'No se pudo conectar a Dynamics 365 OData: {exc}') from exc
        if response.status_code != 200:
            raise DynamicsODataError(f'Error OData {response.status_code}: {response.text}', status_code=response.status_code)
        try:
            data = response.json()
        except ValueError as exc:
            raise DynamicsODataError('La respuesta OData no es JSON válido') from exc
        if 'value' not in data and '@odata.nextLink' not in data:
            raise DynamicsODataError("La respuesta OData no contiene el campo 'value' esperado")
        return data
