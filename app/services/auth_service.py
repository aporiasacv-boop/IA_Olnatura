from dataclasses import dataclass
from app.domain.auth import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.password_service import PasswordService

@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    role: UserRole

class AuthService:

    def __init__(self, repository: UserRepository, password_service: PasswordService | None=None):
        self._repository = repository
        self._password_service = password_service or PasswordService()

    def authenticate(self, username: str, password: str) -> AuthenticatedUser | None:
        user = self._repository.get_by_username(username.strip().lower())
        if user is None or not user.is_active:
            return None
        if not self._password_service.verify_password(password, user.password_hash):
            return None
        return self._to_authenticated_user(user)

    def create_user(self, username: str, password: str, role: str) -> User:
        normalized_role = UserRole(role).value
        password_hash = self._password_service.hash_password(password)
        return self._repository.create(
            username=username.strip().lower(),
            password_hash=password_hash,
            role=normalized_role,
        )

    def get_user_by_id(self, user_id: int) -> AuthenticatedUser | None:
        user = self._repository.get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return self._to_authenticated_user(user)

    @staticmethod
    def _to_authenticated_user(user: User) -> AuthenticatedUser:
        return AuthenticatedUser(id=user.id, username=user.username, role=UserRole(user.role))
