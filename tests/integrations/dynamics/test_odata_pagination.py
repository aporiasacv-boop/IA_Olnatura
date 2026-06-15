"""
Pruebas de paginación OData fetch_all_entity.
"""

from unittest.mock import MagicMock

from app.integrations.dynamics.odata_client import DynamicsODataClient, ODataClientConfig


def test_fetch_all_entity_follows_next_link() -> None:
    """Verifica paginación mediante @odata.nextLink."""
    http_client = MagicMock()
    oauth = MagicMock()
    oauth.get_access_token.return_value = "token"

    first_response = MagicMock()
    first_response.status_code = 200
    first_response.json.return_value = {
        "value": [{"CustomerAccount": "C001"}],
        "@odata.nextLink": "https://example.operations.dynamics.com/data/CustomersV3?$skiptoken=abc",
    }

    second_response = MagicMock()
    second_response.status_code = 200
    second_response.json.return_value = {
        "value": [{"CustomerAccount": "C002"}],
    }

    http_client.get.side_effect = [first_response, second_response]

    client = DynamicsODataClient(
        config=ODataClientConfig(
            base_url="https://example.operations.dynamics.com/data",
            health_entity="Companies",
        ),
        oauth_provider=oauth,
        http_client=http_client,
    )

    records = client.fetch_all_entity("CustomersV3", page_size=1)

    assert len(records) == 2
    assert records[0]["CustomerAccount"] == "C001"
    assert records[1]["CustomerAccount"] == "C002"
    assert http_client.get.call_count == 2
