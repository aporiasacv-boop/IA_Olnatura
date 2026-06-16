from fastapi.testclient import TestClient
from app.core.config import settings

def test_health_check_returns_ok(client: TestClient) -> None:
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert data['app_name'] == settings.APP_NAME
    assert data['version'] == settings.APP_VERSION
