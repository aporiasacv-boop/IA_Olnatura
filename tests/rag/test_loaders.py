import pytest
from app.rag.exceptions import UnsupportedDocumentError
from app.rag.loaders import load_document, validate_extension

def test_validate_extension_accepts_pdf_and_docx() -> None:
    assert validate_extension('informe.pdf') == '.pdf'
    assert validate_extension('manual.DOCX') == '.docx'

def test_validate_extension_rejects_unsupported() -> None:
    with pytest.raises(UnsupportedDocumentError, match='Formato no soportado'):
        validate_extension('archivo.txt')

def test_load_document_docx_with_mock(tmp_path, monkeypatch) -> None:
    from langchain_core.documents import Document
    file_path = tmp_path / 'test.docx'
    file_path.write_bytes(b'fake-docx')

    class FakeLoader:

        def __init__(self, path: str):
            self.path = path

        def load(self):
            return [Document(page_content='Contenido de prueba DOCX', metadata={})]
    monkeypatch.setattr('app.rag.loaders.Docx2txtLoader', FakeLoader)
    docs = load_document(str(file_path), 'test.docx')
    assert len(docs) == 1
    assert docs[0].page_content == 'Contenido de prueba DOCX'
    assert docs[0].metadata['source'] == 'test.docx'
