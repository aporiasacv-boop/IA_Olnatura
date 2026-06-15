"""Excepciones del sistema RAG."""


class RAGError(Exception):
    """Error base del sistema RAG."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedDocumentError(RAGError):
    """Formato de documento no soportado."""


class DocumentLoadError(RAGError):
    """Error al cargar o procesar un documento."""
