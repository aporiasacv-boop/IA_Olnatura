from pathlib import Path
import pytest
from app.documents.exceptions import DocumentNotFoundError, UnsupportedDocumentFormatError
from app.documents.text_extractor import extract_text, validate_document_extension
from app.services.document_loader_service import DocumentLoaderService

def test_validate_document_extension_accepts_supported_formats() -> None:
    assert validate_document_extension('manual.pdf') == '.pdf'
    assert validate_document_extension('acta.DOCX') == '.docx'
    assert validate_document_extension('notas.txt') == '.txt'

def test_validate_document_extension_rejects_unsupported() -> None:
    with pytest.raises(UnsupportedDocumentFormatError, match='Formato no soportado'):
        validate_document_extension('imagen.png')

def test_extract_text_reads_txt_file(tmp_path: Path) -> None:
    file_path = tmp_path / 'manual.txt'
    file_path.write_text('Contenido de prueba para el document loader.', encoding='utf-8')
    assert extract_text(file_path) == 'Contenido de prueba para el document loader.'

def test_document_loader_service_lists_supported_files(tmp_path: Path) -> None:
    (tmp_path / 'Manual_de_procesos.docx').write_bytes(b'')
    (tmp_path / 'Acta_Constitutiva.docx').write_bytes(b'')
    (tmp_path / 'notas.txt').write_text('hola', encoding='utf-8')
    (tmp_path / 'ignorar.png').write_bytes(b'')
    service = DocumentLoaderService(tmp_path)
    assert service.list_documents() == ['Acta_Constitutiva.docx', 'Manual_de_procesos.docx', 'notas.txt']

def test_document_loader_service_reload_updates_catalog(tmp_path: Path) -> None:
    service = DocumentLoaderService(tmp_path)
    assert service.list_documents() == []
    (tmp_path / 'nuevo.txt').write_text('documento nuevo', encoding='utf-8')
    reloaded = service.reload()
    assert reloaded == ['nuevo.txt']
    assert service.list_documents() == ['nuevo.txt']

def test_document_loader_service_preview_limits_characters(tmp_path: Path) -> None:
    (tmp_path / 'largo.txt').write_text('a' * 2500, encoding='utf-8')
    service = DocumentLoaderService(tmp_path)
    document_name, preview = service.preview('largo.txt')
    assert document_name == 'largo.txt'
    assert len(preview) == DocumentLoaderService.PREVIEW_MAX_CHARS

def test_document_loader_service_rejects_unknown_document(tmp_path: Path) -> None:
    service = DocumentLoaderService(tmp_path)
    with pytest.raises(DocumentNotFoundError):
        service.preview('inexistente.txt')

def test_document_loader_service_blocks_path_traversal(tmp_path: Path) -> None:
    (tmp_path / 'seguro.txt').write_text('ok', encoding='utf-8')
    service = DocumentLoaderService(tmp_path)
    with pytest.raises(DocumentNotFoundError):
        service.preview('../../outside.txt')
