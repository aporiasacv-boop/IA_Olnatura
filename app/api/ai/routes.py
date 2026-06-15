"""
Endpoints de inteligencia artificial (Ollama).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_ai_service, get_business_interpretation_service
from app.core.logging import get_logger
from app.integrations.ollama.exceptions import OllamaError
from app.schemas.ai import (
    AITestRequest,
    AITestResponse,
    BusinessSummaryRequest,
    BusinessSummaryResponse,
)
from app.services.ai_service import AIService
from app.services.business_interpretation_service import BusinessInterpretationService

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/test",
    response_model=AITestResponse,
    summary="Probar inferencia con Ollama",
    tags=["AI"],
)
def test_ai(
    request: AITestRequest,
    service: AIService = Depends(get_ai_service),
) -> AITestResponse:
    """
    Envía un prompt al modelo Ollama configurado y retorna la respuesta.

    Retorna 503 si Ollama no está disponible o falla la inferencia.
    """
    logger.info("Solicitud de prueba AI recibida")
    try:
        response = service.test_prompt(request.prompt)
    except OllamaError as exc:
        logger.error("Error en inferencia Ollama: %s", exc.message)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc

    return AITestResponse(response=response)


@router.post(
    "/business-summary",
    response_model=BusinessSummaryResponse,
    summary="Interpretación empresarial de indicadores",
    tags=["AI"],
)
def business_summary(
    request: BusinessSummaryRequest,
    service: BusinessInterpretationService = Depends(get_business_interpretation_service),
) -> BusinessSummaryResponse:
    """
    Interpreta indicadores de ventas y clientes mediante LLM.

    Genera un prompt estructurado bajo reglas estrictas:
    solo interpretar y resumir, sin recomendar acciones ni tomar decisiones.

    Retorna 503 si Ollama no está disponible.
    """
    logger.info(
        "Interpretación empresarial solicitada — ventas_mes=%s, clientes=%s",
        request.ventas_mes,
        request.clientes,
    )
    try:
        summary = service.generate_summary(
            ventas_mes=request.ventas_mes,
            clientes=request.clientes,
        )
    except OllamaError as exc:
        logger.error("Error en interpretación empresarial: %s", exc.message)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc

    return BusinessSummaryResponse(summary=summary)
