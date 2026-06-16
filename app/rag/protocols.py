from typing import Any, Protocol
from langchain_core.documents import Document

class VectorStoreProtocol(Protocol):

    def add_documents(self, documents: list[Document]) -> int:
        ...

    def similarity_search(self, query: str, k: int) -> list[Document]:
        ...

class DocumentLoaderProtocol(Protocol):

    def load(self, file_path: str, filename: str) -> list[Document]:
        ...
