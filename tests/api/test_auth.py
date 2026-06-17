import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.session import get_db
from app.domain.auth import UserRole
from app.main import app
from app.models.base import Base
from app.models import user as user_model
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.services.password_service import PasswordService

@pytest.fixture
def auth_db() -> Session:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    auth_service = AuthService(UserRepository(session))
    auth_service.create_user('admin', 'Admin123!', UserRole.ADMIN.value)
    auth_service.create_user('manager', 'Manager123!', UserRole.MANAGER.value)
    auth_service.create_user('user', 'User123!', UserRole.USER.value)
    return session

@pytest.fixture
def auth_client(auth_db: Session, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr('app.core.config.settings.AUTH_ENABLED', True)

    def override_get_db():
        yield auth_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def login(client: TestClient, username: str, password: str) -> None:
    response = client.post('/auth/login', json={'username': username, 'password': password})
    assert response.status_code == 200

def test_login_success(auth_client: TestClient) -> None:
    response = auth_client.post('/auth/login', json={'username': 'admin', 'password': 'Admin123!'})
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'admin'
    assert data['role'] == 'admin'

def test_login_invalid_credentials(auth_client: TestClient) -> None:
    response = auth_client.post('/auth/login', json={'username': 'admin', 'password': 'wrong'})
    assert response.status_code == 401

def test_logout_clears_session(auth_client: TestClient) -> None:
    login(auth_client, 'user', 'User123!')
    response = auth_client.post('/auth/logout')
    assert response.status_code == 200
    me = auth_client.get('/auth/me')
    assert me.status_code == 401

def test_me_returns_current_user(auth_client: TestClient) -> None:
    login(auth_client, 'manager', 'Manager123!')
    response = auth_client.get('/auth/me')
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'manager'
    assert data['role'] == 'manager'

def test_assistant_requires_authentication(auth_client: TestClient) -> None:
    response = auth_client.post('/assistant', json={'question': '¿Cuántos clientes tenemos?'})
    assert response.status_code == 401

def test_ui_redirects_to_login_when_unauthenticated(auth_client: TestClient) -> None:
    response = auth_client.get('/ui/', follow_redirects=False)
    assert response.status_code == 303
    assert response.headers['location'] == '/ui/login.html'

def test_ui_accessible_after_login(auth_client: TestClient) -> None:
    login(auth_client, 'admin', 'Admin123!')
    response = auth_client.get('/ui/')
    assert response.status_code == 200
    assert 'Asistente Empresarial Olnatura' in response.text

def test_login_page_is_public(auth_client: TestClient) -> None:
    response = auth_client.get('/ui/login.html')
    assert response.status_code == 200
    assert 'Iniciar sesión' in response.text

def test_logout_redirect(auth_client: TestClient) -> None:
    login(auth_client, 'admin', 'Admin123!')
    response = auth_client.get('/auth/logout', follow_redirects=False)
    assert response.status_code == 303
    assert response.headers['location'] == '/ui/login.html'
