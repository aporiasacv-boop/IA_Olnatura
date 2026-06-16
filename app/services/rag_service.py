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
    filename: str
    chunks_indexed: int
    status: str = 'indexed'

@dataclass(frozen=True)
class SourceChunk:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class QueryResult:
    answer: str
    sources: list[SourceChunk] = field(default_factory=list)

class RAGService:

    def __init__(self, vector_store: VectorStoreProtocol, llm_client: LLMClient, app_settings: Settings | None=None):
        self._vector_store = vector_store
        self._llm_client = llm_client
        self._settings = app_settings or settings

    def index_file(self, file_path: str, filename: str) -> IndexResult:
        documents = load_document(file_path, filename)
        chunks = split_documents(documents, chunk_size=self._settings.RAG_CHUNK_SIZE, chunk_overlap=self._settings.RAG_CHUNK_OVERLAP)
        indexed = self._vector_store.add_documents(chunks)
        return IndexResult(filename=filename, chunks_indexed=indexed)

    def query(self, question: str, top_k: int | None=None) -> QueryResult:
        k = top_k if top_k is not None else self._settings.RAG_TOP_K
        retrieved = self._vector_store.similarity_search(question, k=k)
        if not retrieved:
            return QueryResult(answer='No se encontraron documentos indexados relevantes para responder.', sources=[])
        context = '\n\n'.join((doc.page_content for doc in retrieved))
        prompt = build_rag_prompt(context, question)
        answer = self._llm_client.generate(prompt)
        return QueryResult(answer=answer, sources=[self._to_source_chunk(doc) for doc in retrieved])

    @staticmethod
    def _to_source_chunk(document: Document) -> SourceChunk:
        return SourceChunk(content=document.page_content, metadata=dict(document.metadata))
