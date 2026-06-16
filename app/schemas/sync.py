from pydantic import BaseModel, Field

class EntitySyncResponse(BaseModel):
    extracted: int = Field(..., description='Registros extraídos de OData')
    upserted: int = Field(..., description='Registros insertados o actualizados')

class SyncResponse(BaseModel):
    status: str = Field(..., description='Estado: completed | completed_with_errors')
    clientes: EntitySyncResponse
    ventas: EntitySyncResponse
    errors: list[str] = Field(default_factory=list, description='Errores parciales')

class MvpSyncResponse(BaseModel):
    entity: str = Field(..., description='Etiqueta de la entidad sincronizada')
    read: int = Field(..., description='Registros leídos de OData')
    inserted: int = Field(..., description='Registros insertados')
    updated: int = Field(..., description='Registros actualizados')
    errors: list[str] = Field(default_factory=list, description='Errores durante la sincronización')
