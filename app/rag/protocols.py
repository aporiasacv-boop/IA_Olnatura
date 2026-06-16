from typing import Any, Protocol
from langchain_core.documents import Document

class VectorStoreProtocol(Protocol):

    def add_documents(self, documents: list[Document]) -> int:
        ...

    def similarity_search(self, query: str, k: int) -> list[Document]:
        ...

    def similarity_search_with_score(self, query: str, k: int) -> list[tuple[Document, float]]:
        ...

    def delete_by_document(self, document_name: str) -> None:
        ...

class DocumentLoaderProtocol(Protocol):

    def load(self, file_path: str, filename: str) -> list[Document]:
        ...
