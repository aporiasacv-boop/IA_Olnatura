from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:

    def __init__(self, db: Session):
        self._db = db

    def count(self) -> int:
        return int(self._db.scalar(select(func.count()).select_from(User)) or 0)

    def get_by_username(self, username: str) -> User | None:
        return self._db.scalar(select(User).where(User.username == username))

    def get_by_id(self, user_id: int) -> User | None:
        return self._db.get(User, user_id)

    def create(self, username: str, password_hash: str, role: str, is_active: bool=True) -> User:
        user = User(username=username, password_hash=password_hash, role=role, is_active=is_active)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user
