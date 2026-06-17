from fastapi import APIRouter, Depends

from app.api.deps import DbSession, DynamicsClientDep
from app.core.logging import get_logger
from app.schemas.sync import EntitySyncResponse, MvpSyncResponse, SyncResponse
from app.services.sync_service import EntitySyncResult, SyncService

router = APIRouter()
logger = get_logger(__name__)

def get_sync_service(db: DbSession, dynamics_client: DynamicsClientDep) -> SyncService:
    return SyncService(db=db, dynamics_client=dynamics_client)

def _to_entity_response(result: EntitySyncResult) -> EntitySyncResponse:
    return EntitySyncResponse(
        extracted=result.extracted,
        upserted=result.upserted,
        inserted=result.inserted,
        updated=result.updated,
        duration_seconds=result.duration_seconds,
    )

@router.post('/sync', response_model=SyncResponse, summary='Ejecutar sincronizacion manual Dynamics → PostgreSQL', tags=['Sync'])
def run_sync(service: SyncService = Depends(get_sync_service)) -> SyncResponse:
    logger.info('Sincronizacion manual solicitada via POST /sync')
    result = service.run()
    return SyncResponse(
        status=result.status,
        clientes=_to_entity_response(result.clientes),
        ventas=_to_entity_response(result.ventas),
        venta_lineas=_to_entity_response(result.venta_lineas),
        duration_seconds=result.duration_seconds,
        errors=result.errors,
    )

@router.post('/sync/ventas', response_model=MvpSyncResponse, summary='Sincronizar pedidos de venta Dynamics → PostgreSQL', tags=['Sync'])
def run_sync_ventas(service: SyncService = Depends(get_sync_service)) -> MvpSyncResponse:
    logger.info('Sincronizacion de ventas solicitada via POST /sync/ventas')
    result = service.run_ventas()
    return MvpSyncResponse(
        entity=result.entity,
        read=result.read,
        inserted=result.inserted,
        updated=result.updated,
        duration_seconds=result.duration_seconds,
        errors=result.errors,
    )

@router.post('/sync/ventas-lineas', response_model=MvpSyncResponse, summary='Sincronizar lineas de venta Dynamics → PostgreSQL', tags=['Sync'])
def run_sync_ventas_lineas(service: SyncService = Depends(get_sync_service)) -> MvpSyncResponse:
    logger.info('Sincronizacion de lineas de venta solicitada via POST /sync/ventas-lineas')
    result = service.run_ventas_lineas()
    return MvpSyncResponse(
        entity=result.entity,
        read=result.read,
        inserted=result.inserted,
        updated=result.updated,
        duration_seconds=result.duration_seconds,
        errors=result.errors,
    )
