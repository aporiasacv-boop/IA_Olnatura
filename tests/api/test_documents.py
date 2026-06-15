"""
Pruebas de endpoints RAG /documents.
"""

from io import BytesIO
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.deps import get_rag_service
from app.integrations.ollama.exceptions import OllamaConnectionError
from app.main import app
from app.services.rag_service import IndexResult, QueryResult, RAGService, SourceChunk


def test_post_documents_index_success() -> None:
    """Verifica indexación exitosa de documento."""
    mock_service = MagicMock(spec=RAGService)
    mock_service.index_file.return_value = IndexResult(
        filename="informe.pdf",
        chunks_indexed=5,
    )

    app.dependency_overrides[get_rag_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/documents/index",
                files={"file": ("informe.pdf", BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "informe.pdf"
    assert data["chunks_indexed"] == 5
    assert data["status"] == "indexed"


def test_post_documents_index_rejects_unsupported_format() -> None:
    """Verifica rechazo de formatos no soportados."""
    with TestClient(app) as client:
        response = client.post(
            "/documents/index",
            files={"file": ("notas.txt", BytesIO(b"hola"), "text/plain")},
        )

    assert response.status_code == 400
    assert "Formato no soportado" in response.json()["detail"]


def test_post_documents_query_success() -> None:
    """Verifica consulta RAG exitosa."""
    mock_service = MagicMock(spec=RAGService)
    mock_service.query.return_value = QueryResult(
        answer="La política de ventas establece metas trimestrales.",
        sources=[SourceChunk(content="fragmento", metadata={"source": "manual.docx"})],
    )

    app.dependency_overrides[get_rag_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/documents/query",
                json={"question": "¿Cuál es la política de ventas?"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "política de ventas" in data["answer"].lower()
    assert len(data["sources"]) == 1
    mock_service.query.assert_called_once_with("¿Cuál es la política de ventas?", top_k=None)


def test_post_documents_query_returns_503_on_llm_error() -> None:
    """Verifica HTTP 503 cuando Ollama falla."""
    mock_service = MagicMock(spec=RAGService)
    mock_service.query.side_effect = OllamaConnectionError("No se pudo conectar con Ollama")

    app.dependency_overrides[get_rag_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/documents/query",
                json={"question": "¿Algo?"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
