import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.domain.auth import UserRole
from app.models.base import Base
from app.models import user as user_model
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

@pytest.fixture
def auth_service() -> AuthService:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    return AuthService(UserRepository(session))

def test_authenticate_valid_user(auth_service: AuthService) -> None:
    auth_service.create_user('admin', 'Admin123!', UserRole.ADMIN.value)
    user = auth_service.authenticate('admin', 'Admin123!')
    assert user is not None
    assert user.username == 'admin'
    assert user.role == UserRole.ADMIN

def test_authenticate_rejects_invalid_password(auth_service: AuthService) -> None:
    auth_service.create_user('user', 'User123!', UserRole.USER.value)
    assert auth_service.authenticate('user', 'wrong') is None

def test_authenticate_normalizes_username(auth_service: AuthService) -> None:
    auth_service.create_user('Manager', 'Manager123!', UserRole.MANAGER.value)
    user = auth_service.authenticate('MANAGER', 'Manager123!')
    assert user is not None
    assert user.username == 'manager'
