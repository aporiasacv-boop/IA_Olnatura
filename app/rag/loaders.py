from pathlib import Path
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.documents import Document
from app.rag.exceptions import DocumentLoadError, UnsupportedDocumentError
SUPPORTED_EXTENSIONS = {'.pdf', '.docx'}

def validate_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(f'Formato no soportado: {extension}. Use PDF o DOCX.')
    return extension

def load_document(file_path: str, filename: str) -> list[Document]:
    extension = validate_extension(filename)
    try:
        if extension == '.pdf':
            loader = PyPDFLoader(file_path)
        else:
            loader = Docx2txtLoader(file_path)
        documents = loader.load()
    except Exception as exc:
        raise DocumentLoadError(f"No se pudo cargar '{filename}': {exc}") from exc
    for doc in documents:
        doc.metadata['source'] = filename
    if not documents:
        raise DocumentLoadError(f"El documento '{filename}' no contiene texto extraíble.")
    return documents
