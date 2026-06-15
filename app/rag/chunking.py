"""
División de documentos en chunks para indexación RAG.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents: list[Document],
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """
    Divide documentos en fragmentos solapados.

    Args:
        documents: Documentos LangChain originales.
        chunk_size: Tamaño máximo de cada chunk.
        chunk_overlap: Solapamiento entre chunks consecutivos.

    Returns:
        Lista de chunks listos para indexar.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(documents)
