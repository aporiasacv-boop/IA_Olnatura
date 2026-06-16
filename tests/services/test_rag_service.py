from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from app.services.rag_service import RAGService

def test_index_file_loads_splits_and_indexes() -> None:
    vector_store = MagicMock()
    vector_store.add_documents.return_value = 2
    llm = MagicMock()
    service = RAGService(vector_store, llm)
    documents = [Document(page_content='Texto largo del documento', metadata={'source': 'doc.pdf'})]
    chunks = [Document(page_content='chunk 1', metadata={'source': 'doc.pdf'}), Document(page_content='chunk 2', metadata={'source': 'doc.pdf'})]
    with patch('app.services.rag_service.load_document', return_value=documents):
        with patch('app.services.rag_service.split_documents', return_value=chunks):
            result = service.index_file('/tmp/doc.pdf', 'doc.pdf')
    assert result.filename == 'doc.pdf'
    assert result.chunks_indexed == 2
    assert result.status == 'indexed'
    vector_store.add_documents.assert_called_once_with(chunks)

def test_query_retrieves_context_and_generates_answer() -> None:
    vector_store = MagicMock()
    vector_store.similarity_search.return_value = [Document(page_content='Política de ventas Q2', metadata={'source': 'manual.docx'})]
    llm = MagicMock()
    llm.generate.return_value = 'La política de ventas indica objetivos trimestrales.'
    service = RAGService(vector_store, llm)
    result = service.query('¿Cuál es la política de ventas?', top_k=3)
    assert 'política de ventas' in result.answer.lower()
    assert len(result.sources) == 1
    assert result.sources[0].metadata['source'] == 'manual.docx'
    llm.generate.assert_called_once()
    prompt = llm.generate.call_args[0][0]
    assert 'Política de ventas Q2' in prompt
    assert '¿Cuál es la política de ventas?' in prompt

def test_query_returns_message_when_no_documents() -> None:
    vector_store = MagicMock()
    vector_store.similarity_search.return_value = []
    llm = MagicMock()
    service = RAGService(vector_store, llm)
    result = service.query('¿Algo?')
    assert 'no se encontraron' in result.answer.lower()
    llm.generate.assert_not_called()
