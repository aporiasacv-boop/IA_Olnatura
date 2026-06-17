from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.api.deps import get_semantic_search_service
from app.integrations.ollama.exceptions import OllamaConnectionError
from app.main import app
from app.services.semantic_search_service import SemanticIndexResult, SemanticSearchHit, SemanticSearchResult, SemanticSearchService

def test_post_documents_index_success() -> None:
    mock_service = MagicMock(spec=SemanticSearchService)
    mock_service.index_all.return_value = SemanticIndexResult(documents=6, chunks=245, status='indexed')
    app.dependency_overrides[get_semantic_search_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/documents/index')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data == {'documents': 6, 'chunks': 245, 'status': 'indexed'}
    mock_service.index_all.assert_called_once()

def test_post_documents_query_success() -> None:
    mock_service = MagicMock(spec=SemanticSearchService)
    mock_service.search.return_value = SemanticSearchResult(
        query='objeto social de la empresa',
        results=[SemanticSearchHit(document='Acta_Constitutiva.docx', score=0.93, content='El objeto social es...')],
    )
    app.dependency_overrides[get_semantic_search_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/documents/query', json={'query': 'objeto social de la empresa'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['query'] == 'objeto social de la empresa'
    assert len(data['results']) == 1
    assert data['results'][0]['document'] == 'Acta_Constitutiva.docx'
    assert data['results'][0]['score'] == 0.93
    mock_service.search.assert_called_once_with('objeto social de la empresa', top_k=None)

def test_post_documents_query_returns_503_on_ollama_error() -> None:
    mock_service = MagicMock(spec=SemanticSearchService)
    mock_service.search.side_effect = OllamaConnectionError('No se pudo conectar con Ollama')
    app.dependency_overrides[get_semantic_search_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/documents/query', json={'query': 'objeto social'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503

def test_post_documents_query_validates_empty_query() -> None:
    with TestClient(app) as client:
        response = client.post('/documents/query', json={'query': ''})
    assert response.status_code == 422

def test_post_documents_analyze_success() -> None:
    from app.api.deps import get_ai_response_service, get_document_context_service, get_document_insights_service
    from app.domain.document_context import DocumentContext
    from app.domain.document_insights import DocumentInsights
    mock_context_service = MagicMock()
    mock_context_service.build_context.return_value = DocumentContext(
        documents=[{'document_name': 'Manual.pdf', 'score': 0.91, 'content': 'Contenido'}],
        sources=['Manual.pdf'],
        top_document='Manual.pdf',
        total_matches=1,
        average_score=0.91,
        context='[Manual.pdf] contenido',
    )
    mock_insights_service = MagicMock()
    mock_insights_service.build_insights.return_value = DocumentInsights(
        total_matches=1,
        confidence_level='HIGH',
        top_document='Manual.pdf',
        source_documents=['Manual.pdf'],
        average_score=0.91,
    )
    mock_ai = MagicMock()
    mock_ai.generate_document_analysis.return_value = 'Segun Manual.pdf, el analista documenta procesos.'
    app.dependency_overrides[get_document_context_service] = lambda: mock_context_service
    app.dependency_overrides[get_document_insights_service] = lambda: mock_insights_service
    app.dependency_overrides[get_ai_response_service] = lambda: mock_ai
    try:
        with TestClient(app) as client:
            response = client.post('/documents/analyze', json={'query': '¿Qué hace el analista de procesos?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['confidence_level'] == 'HIGH'
    assert data['sources'] == ['Manual.pdf']
    assert 'Manual.pdf' in data['answer']
