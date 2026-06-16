from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse
router = APIRouter()

@router.get('', response_model=HealthResponse, summary='Verificar estado del servicio', description='Retorna el estado operativo de la API y metadatos básicos.')
def health_check() -> HealthResponse:
    return HealthResponse(status='ok', app_name=settings.APP_NAME, version=settings.APP_VERSION)
