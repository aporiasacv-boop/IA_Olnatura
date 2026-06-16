from collections.abc import Generator
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.integrations.dynamics.factory import create_dynamics_client
from app.integrations.dynamics.odata_client import DynamicsODataClient
from app.integrations.ollama.factory import create_ollama_client
from app.integrations.ollama.client import OllamaClient
from app.rag.factory import create_embeddings, create_vector_store
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.business_interpretation_service import BusinessInterpretationService
from app.services.ai_response_service import AIResponseService
from app.services.chat_service import ChatService
from app.services.natural_chat_service import NaturalChatService
from app.services.rag_service import RAGService
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

def get_rag_service(llm_client: OllamaClientDep) -> RAGService:
    embeddings = create_embeddings()
    vector_store = create_vector_store(embeddings)
    return RAGService(vector_store=vector_store, llm_client=llm_client)

def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()
