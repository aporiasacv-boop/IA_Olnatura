from pathlib import Path
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.api.deps import get_document_loader_service
from app.documents.exceptions import DocumentNotFoundError
from app.main import app
from app.services.document_loader_service import DocumentLoaderService

def test_get_documents_lists_catalog(tmp_path: Path) -> None:
    (tmp_path / 'Manual_de_procesos.docx').write_bytes(b'')
    (tmp_path / 'Acta_Constitutiva.docx').write_bytes(b'')
    service = DocumentLoaderService(tmp_path)
    app.dependency_overrides[get_document_loader_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.get('/documents')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {'documents': ['Acta_Constitutiva.docx', 'Manual_de_procesos.docx']}

def test_get_documents_preview_returns_text(tmp_path: Path) -> None:
    (tmp_path / 'manual.txt').write_text('Texto inicial del documento empresarial.', encoding='utf-8')
    service = DocumentLoaderService(tmp_path)
    app.dependency_overrides[get_document_loader_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.get('/documents/preview', params={'name': 'manual.txt'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['document'] == 'manual.txt'
    assert 'Texto inicial' in data['preview']

def test_get_documents_preview_returns_404_for_missing_file(tmp_path: Path) -> None:
    service = DocumentLoaderService(tmp_path)
    app.dependency_overrides[get_document_loader_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.get('/documents/preview', params={'name': 'no_existe.txt'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404

def test_post_documents_reload_updates_catalog(tmp_path: Path) -> None:
    service = DocumentLoaderService(tmp_path)
    (tmp_path / 'nuevo.txt').write_text('contenido', encoding='utf-8')
    app.dependency_overrides[get_document_loader_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post('/documents/reload')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {'documents': ['nuevo.txt']}

def test_get_documents_with_mocked_service() -> None:
    mock_service = MagicMock(spec=DocumentLoaderService)
    mock_service.list_documents.return_value = ['Manual_de_procesos.docx']
    app.dependency_overrides[get_document_loader_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/documents')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()['documents'] == ['Manual_de_procesos.docx']

def test_get_documents_preview_with_mocked_service() -> None:
    mock_service = MagicMock(spec=DocumentLoaderService)
    mock_service.preview.return_value = ('Manual_de_procesos.docx', 'primeros 2000 caracteres...')
    app.dependency_overrides[get_document_loader_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/documents/preview', params={'name': 'Manual_de_procesos.docx'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()['preview'] == 'primeros 2000 caracteres...'

def test_get_documents_preview_returns_404_with_mocked_not_found() -> None:
    mock_service = MagicMock(spec=DocumentLoaderService)
    mock_service.preview.side_effect = DocumentNotFoundError('Documento no encontrado')
    app.dependency_overrides[get_document_loader_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/documents/preview', params={'name': 'faltante.txt'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404
