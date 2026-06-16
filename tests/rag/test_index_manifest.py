from pathlib import Path
from app.rag.index_manifest import IndexManifestStore

def test_index_manifest_store_persists_entries(tmp_path: Path) -> None:
    manifest_path = tmp_path / 'chroma' / 'index_manifest.json'
    store = IndexManifestStore(manifest_path)
    assert store.load() == {}
    store.save({'manual.txt': 'hash-1', 'acta.docx': 'hash-2'})
    reloaded = IndexManifestStore(manifest_path)
    assert reloaded.load() == {'manual.txt': 'hash-1', 'acta.docx': 'hash-2'}

def test_index_manifest_store_returns_empty_on_invalid_json(tmp_path: Path) -> None:
    manifest_path = tmp_path / 'index_manifest.json'
    manifest_path.write_text('{invalid', encoding='utf-8')
    store = IndexManifestStore(manifest_path)
    assert store.load() == {}
