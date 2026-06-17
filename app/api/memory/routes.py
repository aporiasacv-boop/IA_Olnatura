from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_snapshot_memory_service
from app.core.logging import get_logger
from app.schemas.memory import (
    MemoryCompareResponse,
    MemoryInsightsResponse,
    MemorySnapshotSaveResponse,
    OrganizationalSnapshotResponse,
)
from app.services.snapshot_memory_service import SnapshotMemoryService

router = APIRouter()
logger = get_logger(__name__)

def _to_snapshot_response(payload: dict[str, object]) -> OrganizationalSnapshotResponse:
    return OrganizationalSnapshotResponse(
        id=int(payload['id']),
        snapshot_date=str(payload['snapshot_date']),
        total_customers=int(payload['total_customers']),
        total_orders=int(payload['total_orders']),
        total_revenue=str(payload['total_revenue']),
        top_customer=payload.get('top_customer'),
        top_customer_share=float(payload['top_customer_share']),
        top_product=payload.get('top_product'),
        top_product_share=float(payload['top_product_share']),
        created_at=str(payload.get('created_at')) if payload.get('created_at') else None,
    )

@router.post('/snapshot', response_model=MemorySnapshotSaveResponse, summary='Guardar snapshot organizacional', tags=['Memory'])
def save_snapshot(service: SnapshotMemoryService=Depends(get_snapshot_memory_service)) -> MemorySnapshotSaveResponse:
    logger.info('Guardado de snapshot organizacional via POST /memory/snapshot')
    saved = service.save_snapshot()
    return MemorySnapshotSaveResponse(snapshot=_to_snapshot_response(saved))

@router.get('/latest', response_model=OrganizationalSnapshotResponse, summary='Ultimo snapshot organizacional', tags=['Memory'])
def get_latest_snapshot(service: SnapshotMemoryService=Depends(get_snapshot_memory_service)) -> OrganizationalSnapshotResponse:
    latest = service.latest_snapshot()
    if latest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No hay snapshots organizacionales guardados')
    return _to_snapshot_response(latest)

@router.get('/compare', response_model=MemoryCompareResponse, summary='Comparar snapshots organizacionales', tags=['Memory'])
def compare_snapshots(service: SnapshotMemoryService=Depends(get_snapshot_memory_service)) -> MemoryCompareResponse:
    comparison = service.compare_snapshots()
    latest = comparison['latest_snapshot']
    previous = comparison['previous_snapshot']
    insights = comparison['memory_insights']
    if latest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No hay snapshots organizacionales para comparar')
    return MemoryCompareResponse(
        latest_snapshot=_to_snapshot_response(latest),
        previous_snapshot=_to_snapshot_response(previous) if previous else None,
        memory_insights=MemoryInsightsResponse(**insights),
    )
