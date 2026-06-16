from collections.abc import Generator
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.db.session import get_db
from app.main import app

def test_db_health_returns_connected(client_with_db: TestClient) -> None:
    response = client_with_db.get('/db-health')
    assert response.status_code == 200
    assert response.json() == {'database': 'connected'}

def test_db_health_returns_503_when_database_unavailable() -> None:
    session = MagicMock()
    session.execute.return_value.scalar.return_value = 0

    def override_get_db_session() -> Generator[MagicMock, None, None]:
        yield session
    app.dependency_overrides[get_db] = override_get_db_session
    try:
        with TestClient(app) as client:
            response = client.get('/db-health')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json()['detail'] == 'Database unavailable'
