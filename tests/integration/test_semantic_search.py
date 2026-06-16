from pathlib import Path
from unittest.mock import MagicMock
from langchain_community.embeddings import FakeEmbeddings
from langchain_core.documents import Document
from app.rag.vector_store import ChromaVectorStore
from app.services.semantic_search_service import SemanticSearchService

def test_semantic_search_integration_indexes_and_queries(tmp_path: Path) -> None:
    docs_dir = tmp_path / 'documents'
    docs_dir.mkdir()
    (docs_dir / 'Acta_Constitutiva.txt').write_text('placeholder', encoding='utf-8')
    chroma_dir = tmp_path / 'chroma'
    settings = type('Settings', (), {
        'CHROMA_PERSIST_DIR': str(chroma_dir),
        'RAG_CHUNK_SIZE': 80,
        'RAG_CHUNK_OVERLAP': 10,
        'RAG_TOP_K': 2,
    })()
    embeddings = FakeEmbeddings(size=16)
    vector_store = ChromaVectorStore(
        persist_directory=str(chroma_dir),
        collection_name='test_semantic_search',
        embeddings=embeddings,
    )
    service = SemanticSearchService(vector_store=vector_store, documents_dir=docs_dir, app_settings=settings)
    acta_text = 'El objeto social de la empresa es la comercializacion de productos naturales.'
    from unittest.mock import patch
    with patch('app.services.semantic_search_service.extract_text', return_value=acta_text):
        index_result = service.index_all()
    assert index_result.documents == 1
    assert index_result.chunks >= 1
    duplicate_result = service.index_all()
    assert duplicate_result.chunks == 0
    search_result = service.search('objeto social de la empresa', top_k=1)
    assert search_result.query == 'objeto social de la empresa'
    assert len(search_result.results) == 1
    assert search_result.results[0].document == 'Acta_Constitutiva.txt'
    assert 'objeto social' in search_result.results[0].content.lower()

def test_chroma_vector_store_delete_and_add_with_ids(tmp_path: Path) -> None:
    embeddings = FakeEmbeddings(size=8)
    store = ChromaVectorStore(
        persist_directory=str(tmp_path / 'chroma'),
        collection_name='vector_store_test',
        embeddings=embeddings,
    )
    documents = [
        Document(page_content='fragmento uno', metadata={'source': 'doc.txt', 'chunk_index': 0}),
        Document(page_content='fragmento dos', metadata={'source': 'doc.txt', 'chunk_index': 1}),
    ]
    added = store.add_documents(documents)
    assert added == 2
    store.delete_by_document('doc.txt')
    results = store.similarity_search('fragmento', k=2)
    assert results == []
