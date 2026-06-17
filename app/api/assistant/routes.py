from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_business_assistant_service
from app.core.logging import get_logger
from app.integrations.ollama.exceptions import OllamaError
from app.rag.exceptions import RAGError
from app.schemas.assistant import AssistantRequest, AssistantResponse, HybridAnalysisRequest, HybridAnalysisResponse
from app.services.business_assistant_service import BusinessAssistantService

router = APIRouter()
logger = get_logger(__name__)

@router.post('', response_model=AssistantResponse, summary='Asistente empresarial unificado', tags=['Assistant'])
def ask_assistant(request: AssistantRequest, service: BusinessAssistantService=Depends(get_business_assistant_service)) -> AssistantResponse:
    logger.info('Pregunta recibida en POST /assistant')
    try:
        result = service.ask(request.question)
    except OllamaError as exc:
        logger.error('Error Ollama en asistente empresarial: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    except RAGError as exc:
        logger.error('Error en asistente empresarial: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    return AssistantResponse(source=result.source, answer=result.answer)

@router.post('/hybrid-analysis', response_model=HybridAnalysisResponse, summary='Analisis hibrido empresarial avanzado', tags=['Assistant'])
def analyze_hybrid(request: HybridAnalysisRequest, service: BusinessAssistantService=Depends(get_business_assistant_service)) -> HybridAnalysisResponse:
    logger.info('Pregunta recibida en POST /assistant/hybrid-analysis')
    try:
        result = service.analyze_hybrid(request.question)
    except OllamaError as exc:
        logger.error('Error Ollama en analisis hibrido: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    except RAGError as exc:
        logger.error('Error en analisis hibrido: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    return HybridAnalysisResponse(
        confidence=result.confidence,
        sources=result.sources,
        answer=result.answer,
    )
