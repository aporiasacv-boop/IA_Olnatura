"""
Contratos desacoplados del sistema RAG.
"""

from typing import Any, Protocol

from langchain_core.documents import Document


class VectorStoreProtocol(Protocol):
    """Contrato para almacenamiento vectorial."""

    def add_documents(self, documents: list[Document]) -> int:
        """Indexa documentos y retorna cantidad indexada."""
        ...

    def similarity_search(self, query: str, k: int) -> list[Document]:
        """Busca documentos similares a la consulta."""
        ...


class DocumentLoaderProtocol(Protocol):
    """Contrato para carga de documentos."""

    def load(self, file_path: str, filename: str) -> list[Document]:
        """Carga un archivo y retorna documentos LangChain."""
        ...
