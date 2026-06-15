"""
Schema de respuesta para el health check de base de datos.
"""

from pydantic import BaseModel, Field


class DbHealthResponse(BaseModel):
    """Estado de conectividad con PostgreSQL."""

    database: str = Field(
        ...,
        description="Estado de la conexión a la base de datos",
        examples=["connected"],
    )
