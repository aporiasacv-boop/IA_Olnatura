"""
Endpoint de health check.

Permite verificar que la API está en ejecución.
No requiere autenticación ni acceso a base de datos.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Verificar estado del servicio",
    description="Retorna el estado operativo de la API y metadatos básicos.",
)
def health_check() -> HealthResponse:
    """
    Health check básico.

    Útil para balanceadores de carga, monitoreo y despliegues.
    """
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
