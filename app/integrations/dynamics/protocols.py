from typing import Any, Protocol

class OAuthTokenProvider(Protocol):

    def get_access_token(self) -> str:
        ...

class DynamicsClient(Protocol):

    def ping(self) -> None:
        ...

    def query_entity(self, entity_name: str, top: int=1) -> dict[str, Any]:
        ...

    def fetch_all_entity(self, entity_name: str, page_size: int=100) -> list[dict[str, Any]]:
        ...
