from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_chat_service, get_natural_chat_service
from app.core.logging import get_logger
from app.integrations.ollama.exceptions import OllamaError
from app.schemas.chat import ChatNaturalResponse, ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.natural_chat_service import NaturalChatService

router = APIRouter()
logger = get_logger(__name__)

@router.post('', response_model=ChatResponse, summary='Chat empresarial basado en reglas', tags=['Chat'])
def chat(request: ChatRequest, service: ChatService=Depends(get_chat_service)) -> ChatResponse:
    logger.info('Pregunta recibida en POST /chat')
    result = service.process(request.question)
    return ChatResponse(question=result.question, intent=result.intent.value, data=result.data)

@router.post('/natural', response_model=ChatNaturalResponse, summary='Chat empresarial con respuesta en lenguaje natural', tags=['Chat'])
def chat_natural(request: ChatRequest, service: NaturalChatService=Depends(get_natural_chat_service)) -> ChatNaturalResponse:
    logger.info('Pregunta recibida en POST /chat/natural')
    try:
        result = service.process(request.question)
    except OllamaError as exc:
        logger.error('Error Ollama en chat natural: %s', exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    return ChatNaturalResponse(question=result.question, intent=result.intent, answer=result.answer)
