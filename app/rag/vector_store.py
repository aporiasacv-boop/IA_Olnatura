"""
Almacén vectorial ChromaDB desacoplado.
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.rag.protocols import VectorStoreProtocol


class ChromaVectorStore:
    """
    Wrapper de ChromaDB vía LangChain.

    Persiste embeddings en disco y expone búsqueda por similitud.
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        embeddings: Embeddings,
    ):
        self._store = Chroma(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )

    def add_documents(self, documents: list[Document]) -> int:
        """Indexa documentos en ChromaDB."""
        if not documents:
            return 0
        ids = self._store.add_documents(documents)
        return len(ids)

    def similarity_search(self, query: str, k: int) -> list[Document]:
        """Retorna los k fragmentos más relevantes."""
        if k <= 0:
            return []
        return self._store.similarity_search(query, k=k)
