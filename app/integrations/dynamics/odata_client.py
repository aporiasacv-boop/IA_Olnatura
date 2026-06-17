from dataclasses import dataclass
import time
from typing import Any

import httpx

from app.integrations.dynamics.exceptions import DynamicsConnectionError, DynamicsODataError
from app.integrations.dynamics.protocols import OAuthTokenProvider

@dataclass(frozen=True)
class ODataClientConfig:
    base_url: str
    health_entity: str
    timeout: float = 30.0

@dataclass(frozen=True)
class EntityPaginationStats:
    total_records: int
    pages_traversed: int
    next_links_found: int
    records_per_page: tuple[int, ...]
    duration_seconds: float
    last_page_had_next_link: bool

class DynamicsODataClient:

    def __init__(self, config: ODataClientConfig, oauth_provider: OAuthTokenProvider, http_client: httpx.Client | None = None):
        self._config = config
        self._oauth_provider = oauth_provider
        self._http_client = http_client or httpx.Client(timeout=config.timeout)

    def ping(self) -> None:
        self.query_entity(self._config.health_entity, top=1)

    def query_entity(self, entity_name: str, top: int = 1) -> dict[str, Any]:
        url = f"{self._config.base_url.rstrip('/')}/{entity_name}"
        return self._request_odata(url, params={'$top': top})

    def fetch_all_entity(
        self,
        entity_name: str,
        page_size: int = 100,
        *,
        odata_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        all_records: list[dict[str, Any]] = []
        next_url: str | None = f"{self._config.base_url.rstrip('/')}/{entity_name}"
        params: dict[str, str | int] | None = {'$top': page_size}
        if odata_filter:
            params['$filter'] = odata_filter
        while next_url:
            data = self._request_odata(next_url, params=params)
            all_records.extend(data.get('value', []))
            next_url = data.get('@odata.nextLink')
            params = None
        return all_records

    def count_entity(self, entity_name: str, *, odata_filter: str | None = None) -> int:
        url = f"{self._config.base_url.rstrip('/')}/{entity_name}/$count"
        params: dict[str, str] | None = None
        if odata_filter:
            params = {'$filter': odata_filter}
        token = self._oauth_provider.get_access_token()
        headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        try:
            response = self._http_client.get(url, headers=headers, params=params)
        except httpx.RequestError as exc:
            raise DynamicsConnectionError(f'No se pudo conectar a Dynamics 365 OData: {exc}') from exc
        if response.status_code != 200:
            raise DynamicsODataError(
                f'Error OData $count {response.status_code}: {response.text}',
                status_code=response.status_code,
            )
        return int(response.text.strip().lstrip('\ufeff'))

    def validate_filter(self, entity_name: str, odata_filter: str | None) -> tuple[bool, str | None]:
        if not odata_filter:
            return True, None
        try:
            url = f"{self._config.base_url.rstrip('/')}/{entity_name}"
            self._request_odata(url, params={'$top': 1, '$filter': odata_filter})
            return True, None
        except DynamicsODataError as exc:
            return False, exc.message

    def paginate_entity_stats(
        self,
        entity_name: str,
        page_size: int = 100,
        *,
        odata_filter: str | None = None,
    ) -> EntityPaginationStats:
        started_at = time.perf_counter()
        total_records = 0
        pages_traversed = 0
        next_links_found = 0
        records_per_page: list[int] = []
        next_url: str | None = f"{self._config.base_url.rstrip('/')}/{entity_name}"
        params: dict[str, str | int] | None = {'$top': page_size}
        if odata_filter:
            params['$filter'] = odata_filter
        last_page_had_next_link = False
        while next_url:
            data = self._request_odata(next_url, params=params)
            batch = data.get('value', [])
            pages_traversed += 1
            records_per_page.append(len(batch))
            total_records += len(batch)
            next_link = data.get('@odata.nextLink')
            if next_link:
                next_links_found += 1
                last_page_had_next_link = True
                next_url = next_link
            else:
                last_page_had_next_link = False
                next_url = None
            params = None
        return EntityPaginationStats(
            total_records=total_records,
            pages_traversed=pages_traversed,
            next_links_found=next_links_found,
            records_per_page=tuple(records_per_page),
            duration_seconds=time.perf_counter() - started_at,
            last_page_had_next_link=last_page_had_next_link,
        )

    def _request_odata(self, url: str, params: dict[str, str | int] | None = None) -> dict[str, Any]:
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
