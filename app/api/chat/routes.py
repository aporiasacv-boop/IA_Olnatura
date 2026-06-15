"""
Endpoint de chat empresarial orquestado.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_chat_orchestrator_service
from app.core.logging import get_logger
from app.integrations.ollama.exceptions import OllamaError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_orchestrator_service import ChatOrchestratorService

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat empresarial orquestado",
    tags=["Chat"],
)
def chat(
    request: ChatRequest,
    service: ChatOrchestratorService = Depends(get_chat_orchestrator_service),
) -> ChatResponse:
    """
    Responde preguntas empresariales enrutando según categoría:

    - **Ventas** → consulta PostgreSQL
    - **Clientes** → consulta PostgreSQL
    - **General** → consulta LLM (Ollama)
    """
    logger.info("Pregunta recibida en POST /chat")
    try:
        answer = service.answer(request.question)
    except OllamaError as exc:
        logger.error("Error LLM en chat: %s", exc.message)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc

    return ChatResponse(answer=answer)
