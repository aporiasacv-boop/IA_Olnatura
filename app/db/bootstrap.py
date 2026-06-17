from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.auth import UserRole
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

def bootstrap_users() -> None:
    if not settings.AUTH_ENABLED:
        return
    db = SessionLocal()
    try:
        repository = UserRepository(db)
        if repository.count() > 0:
            return
        auth_service = AuthService(repository)
        auth_service.create_user(settings.DEFAULT_ADMIN_USERNAME, settings.DEFAULT_ADMIN_PASSWORD, UserRole.ADMIN.value)
        auth_service.create_user('manager', settings.DEFAULT_MANAGER_PASSWORD, UserRole.MANAGER.value)
        auth_service.create_user('user', settings.DEFAULT_USER_PASSWORD, UserRole.USER.value)
    finally:
        db.close()
