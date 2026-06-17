from collections.abc import Generator
from functools import lru_cache
from pathlib import Path
from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.integrations.dynamics.factory import create_dynamics_client
from app.integrations.dynamics.odata_client import DynamicsODataClient
from app.integrations.ollama.factory import create_ollama_client
from app.integrations.ollama.client import OllamaClient
from app.rag.factory import create_embeddings, create_vector_store
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.financial_analytics_repository import FinancialAnalyticsRepository
from app.repositories.user_repository import UserRepository
from app.services.ai_service import AIService
from app.services.analytics_context_service import AnalyticsContextService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService, AuthenticatedUser
from app.services.business_interpretation_service import BusinessInterpretationService
from app.services.ai_response_service import AIResponseService
from app.services.chat_service import ChatService
from app.services.business_assistant_service import BusinessAssistantService
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService
from app.services.copilot_context_service import CopilotContextService
from app.services.copilot_insights_service import CopilotInsightsService
from app.services.document_loader_service import DocumentLoaderService
from app.services.hybrid_context_service import HybridContextService
from app.services.hybrid_insights_service import HybridInsightsService
from app.services.financial_analytics_service import FinancialAnalyticsService
from app.services.natural_chat_service import NaturalChatService
from app.services.rag_service import RAGService
from app.services.semantic_search_service import SemanticSearchService
from app.domain.auth import UserRole

DbSession = Annotated[Session, Depends(get_db)]
DynamicsClientDep = Annotated[DynamicsODataClient, Depends(create_dynamics_client)]
OllamaClientDep = Annotated[OllamaClient, Depends(create_ollama_client)]

def get_analytics_repository(db: DbSession) -> AnalyticsRepository:
    return AnalyticsRepository(db)

def get_analytics_service(repository: AnalyticsRepository=Depends(get_analytics_repository)) -> AnalyticsService:
    return AnalyticsService(repository)

def get_ai_service(llm_client: OllamaClientDep) -> AIService:
    return AIService(llm_client)

def get_business_interpretation_service(llm_client: OllamaClientDep) -> BusinessInterpretationService:
    return BusinessInterpretationService(llm_client)

def get_chat_service(analytics_service: AnalyticsService=Depends(get_analytics_service)) -> ChatService:
    return ChatService(analytics_service=analytics_service)

def get_ai_response_service(llm_client: OllamaClientDep) -> AIResponseService:
    return AIResponseService(llm_client)

def get_natural_chat_service(chat_service: ChatService=Depends(get_chat_service), ai_response_service: AIResponseService=Depends(get_ai_response_service)) -> NaturalChatService:
    return NaturalChatService(chat_service=chat_service, ai_response_service=ai_response_service)

@lru_cache
def get_document_loader_service() -> DocumentLoaderService:
    return DocumentLoaderService(documents_dir=Path(settings.DOCUMENTS_DIR))

@lru_cache
def get_semantic_search_service() -> SemanticSearchService:
    embeddings = create_embeddings()
    vector_store = create_vector_store(embeddings)
    return SemanticSearchService(vector_store=vector_store, documents_dir=Path(settings.DOCUMENTS_DIR))

def get_document_context_service(
    semantic_search_service: SemanticSearchService=Depends(get_semantic_search_service),
) -> DocumentContextService:
    return DocumentContextService(semantic_search_service)

def get_document_insights_service() -> DocumentInsightsService:
    return DocumentInsightsService()

def get_financial_analytics_repository(db: DbSession) -> FinancialAnalyticsRepository:
    return FinancialAnalyticsRepository(db)

def get_financial_analytics_service(
    repository: FinancialAnalyticsRepository=Depends(get_financial_analytics_repository),
) -> FinancialAnalyticsService:
    return FinancialAnalyticsService(repository)

def get_analytics_context_service(
    analytics_service: AnalyticsService=Depends(get_analytics_service),
    financial_analytics_service: FinancialAnalyticsService=Depends(get_financial_analytics_service),
) -> AnalyticsContextService:
    return AnalyticsContextService(
        analytics_service=analytics_service,
        financial_analytics_service=financial_analytics_service,
    )

def get_hybrid_context_service(
    analytics_context_service: AnalyticsContextService=Depends(get_analytics_context_service),
    document_context_service: DocumentContextService=Depends(get_document_context_service),
    document_insights_service: DocumentInsightsService=Depends(get_document_insights_service),
) -> HybridContextService:
    return HybridContextService(
        analytics_context_service,
        document_context_service,
        document_insights_service,
    )

def get_hybrid_insights_service() -> HybridInsightsService:
    return HybridInsightsService()

def get_copilot_insights_service() -> CopilotInsightsService:
    return CopilotInsightsService()

def get_copilot_context_service(
    hybrid_context_service: HybridContextService=Depends(get_hybrid_context_service),
    hybrid_insights_service: HybridInsightsService=Depends(get_hybrid_insights_service),
    copilot_insights_service: CopilotInsightsService=Depends(get_copilot_insights_service),
) -> CopilotContextService:
    return CopilotContextService(
        hybrid_context_service,
        hybrid_insights_service,
        copilot_insights_service,
    )

def get_business_assistant_service(
    chat_service: ChatService=Depends(get_chat_service),
    semantic_search_service: SemanticSearchService=Depends(get_semantic_search_service),
    ai_response_service: AIResponseService=Depends(get_ai_response_service),
    analytics_context_service: AnalyticsContextService=Depends(get_analytics_context_service),
    document_context_service: DocumentContextService=Depends(get_document_context_service),
    document_insights_service: DocumentInsightsService=Depends(get_document_insights_service),
    hybrid_context_service: HybridContextService=Depends(get_hybrid_context_service),
    hybrid_insights_service: HybridInsightsService=Depends(get_hybrid_insights_service),
    copilot_context_service: CopilotContextService=Depends(get_copilot_context_service),
) -> BusinessAssistantService:
    return BusinessAssistantService(
        chat_service=chat_service,
        semantic_search_service=semantic_search_service,
        ai_response_service=ai_response_service,
        analytics_context_service=analytics_context_service,
        document_context_service=document_context_service,
        document_insights_service=document_insights_service,
        hybrid_context_service=hybrid_context_service,
        hybrid_insights_service=hybrid_insights_service,
        copilot_context_service=copilot_context_service,
    )

def get_rag_service(llm_client: OllamaClientDep) -> RAGService:
    embeddings = create_embeddings()
    vector_store = create_vector_store(embeddings)
    return RAGService(vector_store=vector_store, llm_client=llm_client)

def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()

def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)

def get_auth_service(repository: UserRepository=Depends(get_user_repository)) -> AuthService:
    return AuthService(repository)

def get_current_user(request: Request, db: DbSession) -> AuthenticatedUser:
    if not settings.AUTH_ENABLED:
        return AuthenticatedUser(id=0, username='test', role=UserRole.ADMIN)
    user_id = request.session.get('user_id')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='No autenticado')
    auth_service = AuthService(UserRepository(db))
    user = auth_service.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='No autenticado')
    return user

CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]
