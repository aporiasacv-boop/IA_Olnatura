from fastapi.testclient import TestClient
from app.core.config import settings

def test_root_returns_welcome_message(client: TestClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert 'Bienvenido' in data['message']
    assert data['app_name'] == settings.APP_NAME
    assert data['version'] == settings.APP_VERSION
    assert data['docs_url'] == '/docs'
