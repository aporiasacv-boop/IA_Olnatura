from pathlib import Path
from app.documents.exceptions import DocumentNotFoundError
from app.documents.text_extractor import SUPPORTED_EXTENSIONS, extract_text

class DocumentLoaderService:
    PREVIEW_MAX_CHARS = 2000

    def __init__(self, documents_dir: Path):
        self._documents_dir = documents_dir
        self._catalog: list[str] = []
        self.reload()

    def reload(self) -> list[str]:
        self._documents_dir.mkdir(parents=True, exist_ok=True)
        documents = [path.name for path in sorted(self._documents_dir.iterdir()) if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS]
        self._catalog = documents
        return list(self._catalog)

    def list_documents(self) -> list[str]:
        return list(self._catalog)

    def preview(self, name: str) -> tuple[str, str]:
        document_name = self._resolve_document_name(name)
        file_path = self._documents_dir / document_name
        text = extract_text(file_path)
        return document_name, text[: self.PREVIEW_MAX_CHARS]

    def _resolve_document_name(self, name: str) -> str:
        safe_name = Path(name).name
        if not safe_name or safe_name not in self._catalog:
            raise DocumentNotFoundError(f"Documento no encontrado en el catalogo: '{name}'")
        return safe_name
