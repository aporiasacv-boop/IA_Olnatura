"""
Repositorio base genérico.

Provee operaciones CRUD comunes que los repositorios concretos
pueden extender según cada entidad del dominio.
"""

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.models.base import Base

# TypeVar para tipado genérico del modelo ORM
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repositorio genérico con operaciones básicas de persistencia.

    Args:
        model: Clase del modelo SQLAlchemy asociado a este repositorio.
        db: Sesión activa de SQLAlchemy inyectada por dependencia.
    """

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: int) -> ModelType | None:
        """Obtiene una entidad por su identificador primario."""
        return self.db.get(self.model, entity_id)

    # Los métodos create, update, delete y consultas específicas
    # se implementarán cuando se agregue lógica de negocio.
