"""
Endpoint de sincronización manual ETL.
"""

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, DynamicsClientDep
from app.core.logging import get_logger
from app.schemas.sync import EntitySyncResponse, SyncResponse
from app.services.sync_service import SyncService

router = APIRouter()
logger = get_logger(__name__)


def get_sync_service(
    db: DbSession,
    dynamics_client: DynamicsClientDep,
) -> SyncService:
    """Factory de SyncService para inyección de dependencias."""
    return SyncService(db=db, dynamics_client=dynamics_client)


@router.post(
    "/sync",
    response_model=SyncResponse,
    summary="Ejecutar sincronización manual Dynamics → PostgreSQL",
    tags=["Sync"],
)
def run_sync(service: SyncService = Depends(get_sync_service)) -> SyncResponse:
    """
    Dispara el pipeline ETL completo:

    1. Extrae clientes y ventas vía OData (con reintentos).
    2. Transforma al esquema local.
    3. Realiza upsert en PostgreSQL.
    """
    logger.info("Sincronización manual solicitada vía POST /sync")
    result = service.run()

    return SyncResponse(
        status=result.status,
        clientes=EntitySyncResponse(
            extracted=result.clientes.extracted,
            upserted=result.clientes.upserted,
        ),
        ventas=EntitySyncResponse(
            extracted=result.ventas.extracted,
            upserted=result.ventas.upserted,
        ),
        errors=result.errors,
    )
