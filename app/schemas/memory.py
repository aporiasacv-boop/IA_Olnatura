from pydantic import BaseModel, Field

class OrganizationalSnapshotResponse(BaseModel):
    id: int = Field(..., description='Identificador del snapshot')
    snapshot_date: str = Field(..., description='Fecha del snapshot organizacional')
    total_customers: int = Field(..., description='Total de clientes')
    total_orders: int = Field(..., description='Total de pedidos')
    total_revenue: str = Field(..., description='Ingresos totales registrados')
    top_customer: str | None = Field(None, description='Cliente dominante')
    top_customer_share: float = Field(..., description='Participacion del cliente dominante')
    top_product: str | None = Field(None, description='Producto dominante')
    top_product_share: float = Field(..., description='Participacion del producto dominante')
    created_at: str | None = Field(None, description='Fecha de creacion del registro')

class MemoryInsightsResponse(BaseModel):
    changes: list[str] = Field(default_factory=list)
    stable_findings: list[str] = Field(default_factory=list)
    new_findings: list[str] = Field(default_factory=list)

class MemoryCompareResponse(BaseModel):
    latest_snapshot: OrganizationalSnapshotResponse | None = None
    previous_snapshot: OrganizationalSnapshotResponse | None = None
    memory_insights: MemoryInsightsResponse

class MemorySnapshotSaveResponse(BaseModel):
    snapshot: OrganizationalSnapshotResponse
    message: str = Field(default='Snapshot organizacional guardado')
