"""
Rutas principales de la aplicación mínima.

Expone los endpoints raíz GET / y GET /health.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.health import HealthResponse
from app.schemas.root import RootResponse

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/",
    response_model=RootResponse,
    summary="Información de la API",
    tags=["Root"],
)
def read_root() -> RootResponse:
    """Retorna metadatos básicos de la aplicación."""
    logger.info("Solicitud recibida en GET /")
    return RootResponse(
        message="Bienvenido al Asistente de Inteligencia Empresarial Olnatura",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar estado del servicio",
    tags=["Health"],
)
def health_check() -> HealthResponse:
    """Health check para monitoreo y balanceadores de carga."""
    logger.debug("Health check solicitado")
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
