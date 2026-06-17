from fastapi import APIRouter, Depends
from app.api.deps import DbSession, DynamicsClientDep
from app.core.logging import get_logger
from app.schemas.sync import EntitySyncResponse, MvpSyncResponse, SyncResponse
from app.services.sync_service import SyncService
router = APIRouter()
logger = get_logger(__name__)

def get_sync_service(db: DbSession, dynamics_client: DynamicsClientDep) -> SyncService:
    return SyncService(db=db, dynamics_client=dynamics_client)

@router.post('/sync', response_model=SyncResponse, summary='Ejecutar sincronización manual Dynamics → PostgreSQL', tags=['Sync'])
def run_sync(service: SyncService=Depends(get_sync_service)) -> SyncResponse:
    logger.info('Sincronización manual solicitada vía POST /sync')
    result = service.run()
    return SyncResponse(status=result.status, clientes=EntitySyncResponse(extracted=result.clientes.extracted, upserted=result.clientes.upserted), ventas=EntitySyncResponse(extracted=result.ventas.extracted, upserted=result.ventas.upserted), errors=result.errors)

@router.post('/sync/ventas', response_model=MvpSyncResponse, summary='Sincronizar pedidos de venta Dynamics → PostgreSQL', tags=['Sync'])
def run_sync_ventas(service: SyncService=Depends(get_sync_service)) -> MvpSyncResponse:
    logger.info('Sincronización de ventas solicitada vía POST /sync/ventas')
    result = service.run_ventas()
    return MvpSyncResponse(entity=result.entity, read=result.read, inserted=result.inserted, updated=result.updated, errors=result.errors)

@router.post('/sync/ventas-lineas', response_model=MvpSyncResponse, summary='Sincronizar lineas de venta Dynamics → PostgreSQL', tags=['Sync'])
def run_sync_ventas_lineas(service: SyncService=Depends(get_sync_service)) -> MvpSyncResponse:
    logger.info('Sincronizacion de lineas de venta solicitada via POST /sync/ventas-lineas')
    result = service.run_ventas_lineas()
    return MvpSyncResponse(entity=result.entity, read=result.read, inserted=result.inserted, updated=result.updated, errors=result.errors)
