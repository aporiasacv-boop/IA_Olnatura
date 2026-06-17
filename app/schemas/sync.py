from pydantic import BaseModel, Field

class EntitySyncResponse(BaseModel):
    extracted: int = Field(..., description='Registros extraidos de OData')
    upserted: int = Field(..., description='Registros insertados o actualizados')
    inserted: int = Field(default=0, description='Registros insertados')
    updated: int = Field(default=0, description='Registros actualizados')
    duration_seconds: float = Field(default=0.0, description='Duracion de la sincronizacion de la entidad en segundos')

class SyncResponse(BaseModel):
    status: str = Field(..., description='Estado: completed | completed_with_errors')
    clientes: EntitySyncResponse
    ventas: EntitySyncResponse
    venta_lineas: EntitySyncResponse | None = Field(default=None, description='Metricas de lineas de venta')
    duration_seconds: float = Field(default=0.0, description='Duracion total de la sincronizacion en segundos')
    errors: list[str] = Field(default_factory=list, description='Errores parciales')

class MvpSyncResponse(BaseModel):
    entity: str = Field(..., description='Etiqueta de la entidad sincronizada')
    read: int = Field(..., description='Registros leidos de OData')
    inserted: int = Field(..., description='Registros insertados')
    updated: int = Field(..., description='Registros actualizados')
    duration_seconds: float = Field(default=0.0, description='Duracion de la sincronizacion en segundos')
    errors: list[str] = Field(default_factory=list, description='Errores durante la sincronizacion')
