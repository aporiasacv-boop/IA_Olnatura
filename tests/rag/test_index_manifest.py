from pathlib import Path
from app.rag.index_manifest import IndexManifestStore

def test_index_manifest_store_persists_entries(tmp_path: Path) -> None:
    manifest_path = tmp_path / 'chroma' / 'index_manifest.json'
    store = IndexManifestStore(manifest_path)
    assert store.load() == {}
    store.save({'manual.txt': 'hash-1', 'acta.docx': 'hash-2'})
    reloaded = IndexManifestStore(manifest_path)
    assert reloaded.load() == {'manual.txt': 'hash-1', 'acta.docx': 'hash-2'}

def test_index_manifest_store_persists_metadata_entries(tmp_path: Path) -> None:
    from app.domain.document_metadata import DocumentMetadataEntry
    manifest_path = tmp_path / 'index_manifest.json'
    store = IndexManifestStore(manifest_path)
    entry = DocumentMetadataEntry(
        file_hash='hash-1',
        document_name='manual.pdf',
        document_type='manual',
        file_extension='.pdf',
        indexed_at='2026-01-01T00:00:00+00:00',
        chunk_count=5,
    )
    store.save_entries({'manual.pdf': entry})
    reloaded = IndexManifestStore(manifest_path)
    entries = reloaded.load_entries()
    assert entries['manual.pdf'].chunk_count == 5
    assert entries['manual.pdf'].document_type == 'manual'

def test_index_manifest_store_returns_empty_on_invalid_json(tmp_path: Path) -> None:
    manifest_path = tmp_path / 'index_manifest.json'
    manifest_path.write_text('{invalid', encoding='utf-8')
    store = IndexManifestStore(manifest_path)
    assert store.load() == {}
