from typing import Generic, TypeVar
from sqlalchemy.orm import Session
from app.models.base import Base
ModelType = TypeVar('ModelType', bound=Base)

class BaseRepository(Generic[ModelType]):

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: int) -> ModelType | None:
        return self.db.get(self.model, entity_id)
