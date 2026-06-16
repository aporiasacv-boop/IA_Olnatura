from langchain_core.documents import Document
from app.rag.chunking import split_documents

def test_split_documents_creates_multiple_chunks() -> None:
    long_text = 'palabra ' * 500
    documents = [Document(page_content=long_text, metadata={'source': 'doc.pdf'})]
    chunks = split_documents(documents, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    assert all((chunk.metadata['source'] == 'doc.pdf' for chunk in chunks))
