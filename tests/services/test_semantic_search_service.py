from pathlib import Path
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from app.services.semantic_search_service import SemanticSearchService

def test_index_all_indexes_new_documents(tmp_path: Path) -> None:
    docs_dir = tmp_path / 'documents'
    docs_dir.mkdir()
    (docs_dir / 'manual.txt').write_text('Politica de ventas y operaciones comerciales.', encoding='utf-8')
    chroma_dir = tmp_path / 'chroma'
    vector_store = MagicMock()
    vector_store.add_documents.return_value = 1
    service = SemanticSearchService(vector_store=vector_store, documents_dir=docs_dir, app_settings=type('Settings', (), {'CHROMA_PERSIST_DIR': str(chroma_dir), 'RAG_CHUNK_SIZE': 50, 'RAG_CHUNK_OVERLAP': 10, 'RAG_TOP_K': 4})())
    result = service.index_all()
    assert result.documents == 1
    assert result.chunks == 1
    assert result.status == 'indexed'
    vector_store.add_documents.assert_called_once()
    vector_store.delete_by_document.assert_called_once_with('manual.txt')

def test_index_all_skips_duplicate_documents(tmp_path: Path) -> None:
    docs_dir = tmp_path / 'documents'
    docs_dir.mkdir()
    file_path = docs_dir / 'manual.txt'
    file_path.write_text('Contenido estable para indexacion.', encoding='utf-8')
    chroma_dir = tmp_path / 'chroma'
    vector_store = MagicMock()
    vector_store.add_documents.return_value = 1
    settings = type('Settings', (), {'CHROMA_PERSIST_DIR': str(chroma_dir), 'RAG_CHUNK_SIZE': 100, 'RAG_CHUNK_OVERLAP': 20, 'RAG_TOP_K': 4})()
    service = SemanticSearchService(vector_store=vector_store, documents_dir=docs_dir, app_settings=settings)
    first = service.index_all()
    second = service.index_all()
    assert first.chunks == 1
    assert second.chunks == 0
    assert second.documents == 1
    vector_store.add_documents.assert_called_once()

def test_index_all_reindexes_when_file_changes(tmp_path: Path) -> None:
    docs_dir = tmp_path / 'documents'
    docs_dir.mkdir()
    file_path = docs_dir / 'manual.txt'
    file_path.write_text('Version uno.', encoding='utf-8')
    chroma_dir = tmp_path / 'chroma'
    vector_store = MagicMock()
    vector_store.add_documents.return_value = 1
    settings = type('Settings', (), {'CHROMA_PERSIST_DIR': str(chroma_dir), 'RAG_CHUNK_SIZE': 100, 'RAG_CHUNK_OVERLAP': 20, 'RAG_TOP_K': 4})()
    service = SemanticSearchService(vector_store=vector_store, documents_dir=docs_dir, app_settings=settings)
    service.index_all()
    file_path.write_text('Version dos actualizada.', encoding='utf-8')
    result = service.index_all()
    assert result.chunks == 1
    assert vector_store.delete_by_document.call_count == 2
    assert vector_store.add_documents.call_count == 2

def test_search_returns_ranked_results() -> None:
    vector_store = MagicMock()
    vector_store.similarity_search_with_score.return_value = [
        (Document(page_content='El objeto social de la empresa es comercializar productos naturales.', metadata={'source': 'Acta_Constitutiva.docx'}), 0.07),
    ]
    service = SemanticSearchService(vector_store=vector_store, documents_dir=Path('.'), app_settings=type('Settings', (), {'CHROMA_PERSIST_DIR': './data/chroma', 'RAG_CHUNK_SIZE': 100, 'RAG_CHUNK_OVERLAP': 20, 'RAG_TOP_K': 4})())
    result = service.search('objeto social de la empresa', top_k=3)
    assert result.query == 'objeto social de la empresa'
    assert len(result.results) == 1
    assert result.results[0].document == 'Acta_Constitutiva.docx'
    assert result.results[0].score == 0.93
    vector_store.similarity_search_with_score.assert_called_once_with('objeto social de la empresa', k=3)

def test_index_all_removes_deleted_documents_from_manifest(tmp_path: Path) -> None:
    docs_dir = tmp_path / 'documents'
    docs_dir.mkdir()
    kept = docs_dir / 'activo.txt'
    removed = docs_dir / 'obsoleto.txt'
    kept.write_text('activo', encoding='utf-8')
    removed.write_text('obsoleto', encoding='utf-8')
    chroma_dir = tmp_path / 'chroma'
    vector_store = MagicMock()
    vector_store.add_documents.return_value = 1
    settings = type('Settings', (), {'CHROMA_PERSIST_DIR': str(chroma_dir), 'RAG_CHUNK_SIZE': 100, 'RAG_CHUNK_OVERLAP': 20, 'RAG_TOP_K': 4})()
    service = SemanticSearchService(vector_store=vector_store, documents_dir=docs_dir, app_settings=settings)
    service.index_all()
    removed.unlink()
    result = service.index_all()
    assert result.documents == 1
    vector_store.delete_by_document.assert_any_call('obsoleto.txt')
