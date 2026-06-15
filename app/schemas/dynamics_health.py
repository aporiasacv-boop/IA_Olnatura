"""
Schema de respuesta para el health check de Dynamics 365.
"""

from pydantic import BaseModel, Field


class DynamicsHealthResponse(BaseModel):
    """Estado de conectividad con Dynamics 365 F&O."""

    dynamics: str = Field(
        ...,
        description="Estado de la conexión OData con Dynamics 365",
        examples=["connected"],
    )
