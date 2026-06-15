"""
Servicio RAG: indexación y consulta de documentos empresariales.
"""

from dataclasses import dataclass, field
from typing import Any

from langchain_core.documents import Document

from app.core.config import Settings, settings
from app.integrations.ollama.protocols import LLMClient
from app.rag.chunking import split_documents
from app.rag.loaders import load_document
from app.rag.prompts import build_rag_prompt
from app.rag.protocols import VectorStoreProtocol


@dataclass(frozen=True)
class IndexResult:
    """Resultado de indexación de un documento."""

    filename: str
    chunks_indexed: int
    status: str = "indexed"


@dataclass(frozen=True)
class SourceChunk:
    """Fragmento de documento usado como contexto."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QueryResult:
    """Resultado de una consulta RAG."""

    answer: str
    sources: list[SourceChunk] = field(default_factory=list)


class RAGService:
    """
    Orquesta indexación (PDF/DOCX → ChromaDB) y consultas RAG.

    Usa LangChain para carga/chunking, ChromaDB para vectores
    y Ollama para generación de respuestas.
    """

    def __init__(
        self,
        vector_store: VectorStoreProtocol,
        llm_client: LLMClient,
        app_settings: Settings | None = None,
    ):
        self._vector_store = vector_store
        self._llm_client = llm_client
        self._settings = app_settings or settings

    def index_file(self, file_path: str, filename: str) -> IndexResult:
        """
        Indexa un archivo PDF o DOCX en ChromaDB.

        Args:
            file_path: Ruta al archivo en disco.
            filename: Nombre original del archivo.

        Returns:
            IndexResult con métricas de indexación.
        """
        documents = load_document(file_path, filename)
        chunks = split_documents(
            documents,
            chunk_size=self._settings.RAG_CHUNK_SIZE,
            chunk_overlap=self._settings.RAG_CHUNK_OVERLAP,
        )
        indexed = self._vector_store.add_documents(chunks)
        return IndexResult(filename=filename, chunks_indexed=indexed)

    def query(self, question: str, top_k: int | None = None) -> QueryResult:
        """
        Consulta documentos indexados mediante RAG.

        Args:
            question: Pregunta del usuario.
            top_k: Cantidad de fragmentos a recuperar.

        Returns:
            QueryResult con respuesta y fuentes utilizadas.
        """
        k = top_k if top_k is not None else self._settings.RAG_TOP_K
        retrieved = self._vector_store.similarity_search(question, k=k)

        if not retrieved:
            return QueryResult(
                answer="No se encontraron documentos indexados relevantes para responder.",
                sources=[],
            )

        context = "\n\n".join(doc.page_content for doc in retrieved)
        prompt = build_rag_prompt(context, question)
        answer = self._llm_client.generate(prompt)

        return QueryResult(
            answer=answer,
            sources=[self._to_source_chunk(doc) for doc in retrieved],
        )

    @staticmethod
    def _to_source_chunk(document: Document) -> SourceChunk:
        """Convierte un Document LangChain a SourceChunk."""
        return SourceChunk(
            content=document.page_content,
            metadata=dict(document.metadata),
        )
