from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from app.rag.protocols import VectorStoreProtocol

class ChromaVectorStore:

    def __init__(self, persist_directory: str, collection_name: str, embeddings: Embeddings):
        self._store = Chroma(collection_name=collection_name, persist_directory=persist_directory, embedding_function=embeddings)

    def add_documents(self, documents: list[Document]) -> int:
        if not documents:
            return 0
        ids = [self._build_chunk_id(document, index) for index, document in enumerate(documents)]
        added_ids = self._store.add_documents(documents, ids=ids)
        return len(added_ids)

    def similarity_search(self, query: str, k: int) -> list[Document]:
        if k <= 0:
            return []
        return self._store.similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: int) -> list[tuple[Document, float]]:
        if k <= 0:
            return []
        return self._store.similarity_search_with_score(query, k=k)

    def delete_by_document(self, document_name: str) -> None:
        collection = self._store._collection
        collection.delete(where={'source': document_name})

    def count_chunks(self) -> int:
        return int(self._store._collection.count())

    @staticmethod
    def _build_chunk_id(document: Document, index: int) -> str:
        source = str(document.metadata.get('source', 'document'))
        chunk_index = document.metadata.get('chunk_index', index)
        return f'{source}::{chunk_index}'
