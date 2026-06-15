"""
Rutas de integración con Dynamics 365 Finance & Operations.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DynamicsClientDep
from app.core.logging import get_logger
from app.schemas.dynamics_health import DynamicsHealthResponse
from app.services.dynamics_health import DynamicsHealthService

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/health",
    response_model=DynamicsHealthResponse,
    summary="Verificar conexión a Dynamics 365 F&O",
    tags=["Dynamics"],
)
def dynamics_health_check(client: DynamicsClientDep) -> DynamicsHealthResponse:
    """
    Consulta una entidad OData de prueba para validar conectividad.

    Retorna 503 si Dynamics 365 no responde o falla la autenticación OAuth.
    """
    logger.debug("Dynamics health check solicitado")
    service = DynamicsHealthService(client)

    if not service.is_connected():
        logger.error("Dynamics 365 F&O no respondió correctamente al health check OData")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dynamics unavailable",
        )

    return DynamicsHealthResponse(dynamics="connected")
