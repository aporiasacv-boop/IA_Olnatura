from pathlib import Path
import docx2txt
from pypdf import PdfReader
from app.documents.exceptions import DocumentTextExtractionError, UnsupportedDocumentFormatError

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

def validate_document_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentFormatError(f'Formato no soportado: {extension}. Use PDF, DOCX o TXT.')
    return extension

def extract_text(file_path: Path) -> str:
    extension = validate_document_extension(file_path.name)
    try:
        if extension == '.txt':
            return _read_text_file(file_path)
        if extension == '.pdf':
            return _read_pdf_file(file_path)
        return _read_docx_file(file_path)
    except DocumentTextExtractionError:
        raise
    except Exception as exc:
        raise DocumentTextExtractionError(f"No se pudo extraer texto de '{file_path.name}': {exc}") from exc

def _read_text_file(file_path: Path) -> str:
    for encoding in ('utf-8', 'latin-1'):
        try:
            content = file_path.read_text(encoding=encoding)
            if content.strip():
                return content
        except UnicodeDecodeError:
            continue
    raise DocumentTextExtractionError(f"El archivo TXT '{file_path.name}' no contiene texto legible.")

def _read_pdf_file(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = [page.extract_text() or '' for page in reader.pages]
    content = '\n'.join(pages).strip()
    if not content:
        raise DocumentTextExtractionError(f"El PDF '{file_path.name}' no contiene texto extraible.")
    return content

def _read_docx_file(file_path: Path) -> str:
    content = (docx2txt.process(str(file_path)) or '').strip()
    if not content:
        raise DocumentTextExtractionError(f"El DOCX '{file_path.name}' no contiene texto extraible.")
    return content
