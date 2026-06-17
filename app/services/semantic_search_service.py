import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from langchain_core.documents import Document
from app.core.config import Settings, settings
from app.documents.text_extractor import SUPPORTED_EXTENSIONS, extract_text
from app.domain.document_metadata import DocumentMetadataEntry, infer_document_type, utc_now_iso
from app.rag.chunking import split_documents
from app.rag.index_manifest import IndexManifestStore
from app.rag.protocols import VectorStoreProtocol

@dataclass(frozen=True)
class SemanticIndexResult:
    documents: int
    chunks: int
    status: str = 'indexed'

@dataclass(frozen=True)
class SemanticSearchHit:
    document: str
    score: float
    content: str

@dataclass(frozen=True)
class SemanticSearchResult:
    query: str
    results: list[SemanticSearchHit]

class SemanticSearchService:

    def __init__(self, vector_store: VectorStoreProtocol, documents_dir: Path, app_settings: Settings | None=None, logger: logging.Logger | None=None):
        self._vector_store = vector_store
        self._documents_dir = documents_dir
        self._settings = app_settings or settings
        manifest_path = Path(self._settings.CHROMA_PERSIST_DIR) / 'index_manifest.json'
        self._manifest_store = IndexManifestStore(manifest_path)
        self._logger = logger or logging.getLogger(__name__)

    def index_all(self) -> SemanticIndexResult:
        self._documents_dir.mkdir(parents=True, exist_ok=True)
        entries = self._load_entries()
        current_files = {path.name for path in self._iter_document_files()}
        if not current_files:
            self._logger.warning('No hay documentos indexables en %s', self._documents_dir)
        for stale_name in list(entries.keys()):
            if stale_name not in current_files:
                self._vector_store.delete_by_document(stale_name)
                self._manifest_store.remove_entry(stale_name)
                del entries[stale_name]
        chunks_indexed = 0
        for file_path in self._iter_document_files():
            file_hash = self._file_hash(file_path)
            existing = entries.get(file_path.name)
            if existing is not None and existing.file_hash == file_hash:
                continue
            self._vector_store.delete_by_document(file_path.name)
            text = extract_text(file_path)
            source_documents = [Document(page_content=text, metadata={'source': file_path.name, 'file_hash': file_hash})]
            chunks = split_documents(source_documents, chunk_size=self._settings.RAG_CHUNK_SIZE, chunk_overlap=self._settings.RAG_CHUNK_OVERLAP)
            for index, chunk in enumerate(chunks):
                chunk.metadata['source'] = file_path.name
                chunk.metadata['file_hash'] = file_hash
                chunk.metadata['chunk_index'] = index
            chunk_count = self._vector_store.add_documents(chunks)
            chunks_indexed += chunk_count
            entry = DocumentMetadataEntry(
                file_hash=file_hash,
                document_name=file_path.name,
                document_type=infer_document_type(file_path.name),
                file_extension=file_path.suffix.lower(),
                indexed_at=utc_now_iso(),
                chunk_count=chunk_count,
            )
            self._manifest_store.upsert_entry(entry)
            entries[file_path.name] = entry
        self._logger.info(
            'Indexacion completada documents=%s chunks_nuevos=%s total_chunks=%s',
            len(entries),
            chunks_indexed,
            self._vector_store.count_chunks(),
        )
        return SemanticIndexResult(documents=len(entries), chunks=chunks_indexed, status='indexed')

    def get_metadata_entries(self) -> dict[str, DocumentMetadataEntry]:
        return self._manifest_store.load_entries()

    def _load_entries(self) -> dict[str, DocumentMetadataEntry]:
        entries = self._manifest_store.load_entries()
        if entries and self._vector_store.count_chunks() == 0:
            self._logger.warning('Manifest con entradas pero coleccion Chroma vacia; reiniciando indexacion')
            self._manifest_store.save_entries({})
            return {}
        return entries

    def _load_manifest(self) -> dict[str, str]:
        return {name: entry.file_hash for name, entry in self._load_entries().items()}

    def search(self, query: str, top_k: int | None=None) -> SemanticSearchResult:
        limit = top_k if top_k is not None else self._settings.RAG_TOP_K
        scored_documents = self._vector_store.similarity_search_with_score(query, k=limit)
        results = [SemanticSearchHit(document=str(document.metadata.get('source', 'unknown')), score=self._distance_to_score(distance), content=document.page_content) for document, distance in scored_documents]
        return SemanticSearchResult(query=query, results=results)

    def _iter_document_files(self) -> list[Path]:
        return sorted((path for path in self._documents_dir.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS), key=lambda path: path.name.lower())

    @staticmethod
    def _file_hash(file_path: Path) -> str:
        return hashlib.sha256(file_path.read_bytes()).hexdigest()

    @staticmethod
    def _distance_to_score(distance: float) -> float:
        return round(max(0.0, min(1.0, 1.0 - distance)), 2)
