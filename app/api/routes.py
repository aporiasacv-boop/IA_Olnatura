from fastapi import APIRouter, HTTPException, status
from app.api.deps import DbSession
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.db_health import DbHealthResponse
from app.schemas.health import HealthResponse
from app.schemas.root import RootResponse
from app.services.db_health import DbHealthService
router = APIRouter()
logger = get_logger(__name__)

@router.get('/', response_model=RootResponse, summary='Información de la API', tags=['Root'])
def read_root() -> RootResponse:
    logger.info('Solicitud recibida en GET /')
    return RootResponse(message='Bienvenido al Asistente de Inteligencia Empresarial Olnatura', app_name=settings.APP_NAME, version=settings.APP_VERSION, docs_url='/docs')

@router.get('/health', response_model=HealthResponse, summary='Verificar estado del servicio', tags=['Health'])
def health_check() -> HealthResponse:
    logger.debug('Health check solicitado')
    return HealthResponse(status='ok', app_name=settings.APP_NAME, version=settings.APP_VERSION)

@router.get('/db-health', response_model=DbHealthResponse, summary='Verificar conexión a PostgreSQL', tags=['Health'])
def db_health_check(db: DbSession) -> DbHealthResponse:
    logger.debug('DB health check solicitado')
    service = DbHealthService(db)
    if not service.is_connected():
        logger.error('PostgreSQL no respondió correctamente a SELECT 1')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Database unavailable')
    return DbHealthResponse(database='connected')
