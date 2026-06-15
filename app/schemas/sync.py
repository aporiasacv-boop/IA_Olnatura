"""
Schemas de respuesta para sincronización ETL.
"""

from pydantic import BaseModel, Field


class EntitySyncResponse(BaseModel):
    """Métricas de sincronización por entidad."""

    extracted: int = Field(..., description="Registros extraídos de OData")
    upserted: int = Field(..., description="Registros insertados o actualizados")


class SyncResponse(BaseModel):
    """Resultado de la sincronización manual POST /sync."""

    status: str = Field(..., description="Estado: completed | completed_with_errors")
    clientes: EntitySyncResponse
    ventas: EntitySyncResponse
    errors: list[str] = Field(default_factory=list, description="Errores parciales")
