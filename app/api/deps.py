"""
Dependencias compartidas de la capa API.

Centraliza inyección de dependencias FastAPI reutilizables
en múltiples endpoints (sesión BD, servicios, autenticación futura).
"""

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
from app.services.chat_orchestrator_service import ChatOrchestratorService
from app.services.rag_service import RAGService

# Tipo anotado para inyectar la sesión de BD en endpoints
DbSession = Annotated[Session, Depends(get_db)]

# Tipo anotado para inyectar el cliente OData de Dynamics 365
DynamicsClientDep = Annotated[DynamicsODataClient, Depends(create_dynamics_client)]

# Tipo anotado para inyectar el cliente Ollama
OllamaClientDep = Annotated[OllamaClient, Depends(create_ollama_client)]


def get_analytics_repository(db: DbSession) -> AnalyticsRepository:
    """Factory del repositorio analítico."""
    return AnalyticsRepository(db)


def get_analytics_service(
    repository: AnalyticsRepository = Depends(get_analytics_repository),
) -> AnalyticsService:
    """Factory del servicio de consultas empresariales."""
    return AnalyticsService(repository)


def get_ai_service(
    llm_client: OllamaClientDep,
) -> AIService:
    """Factory del servicio de inteligencia artificial."""
    return AIService(llm_client)


def get_business_interpretation_service(
    llm_client: OllamaClientDep,
) -> BusinessInterpretationService:
    """Factory del servicio de interpretación empresarial."""
    return BusinessInterpretationService(llm_client)


def get_chat_orchestrator_service(
    llm_client: OllamaClientDep,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ChatOrchestratorService:
    """Factory del orquestador de preguntas empresariales."""
    return ChatOrchestratorService(
        analytics_service=analytics_service,
        llm_client=llm_client,
    )


def get_rag_service(llm_client: OllamaClientDep) -> RAGService:
    """Factory del servicio RAG (LangChain + ChromaDB)."""
    embeddings = create_embeddings()
    vector_store = create_vector_store(embeddings)
    return RAGService(vector_store=vector_store, llm_client=llm_client)


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependencia explícita de sesión de base de datos para la capa API.

    Permite extender o reemplazar la dependencia sin modificar endpoints.
    """
    yield from get_db()
