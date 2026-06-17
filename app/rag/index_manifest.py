import json
from pathlib import Path

from app.domain.document_metadata import DocumentMetadataEntry

class IndexManifestStore:

    def __init__(self, manifest_path: Path):
        self._manifest_path = manifest_path

    def load(self) -> dict[str, str]:
        return {name: entry.file_hash for name, entry in self.load_entries().items()}

    def save(self, manifest: dict[str, str]) -> None:
        entries = self.load_entries()
        for name, file_hash in manifest.items():
            if name in entries:
                current = entries[name]
                entries[name] = DocumentMetadataEntry(
                    file_hash=file_hash,
                    document_name=current.document_name,
                    document_type=current.document_type,
                    file_extension=current.file_extension,
                    indexed_at=current.indexed_at,
                    chunk_count=current.chunk_count,
                )
            else:
                entries[name] = DocumentMetadataEntry.from_legacy_hash(name, file_hash)
        self.save_entries(entries)

    def load_entries(self) -> dict[str, DocumentMetadataEntry]:
        if not self._manifest_path.exists():
            return {}
        try:
            data = json.loads(self._manifest_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}
        entries: dict[str, DocumentMetadataEntry] = {}
        for name, value in data.items():
            document_name = str(name)
            if isinstance(value, str):
                entries[document_name] = DocumentMetadataEntry.from_legacy_hash(document_name, value)
            elif isinstance(value, dict):
                entries[document_name] = DocumentMetadataEntry.from_dict(document_name, value)
        return entries

    def save_entries(self, entries: dict[str, DocumentMetadataEntry]) -> None:
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {name: entry.to_dict() for name, entry in entries.items()}
        self._manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    def upsert_entry(self, entry: DocumentMetadataEntry) -> None:
        entries = self.load_entries()
        entries[entry.document_name] = entry
        self.save_entries(entries)

    def remove_entry(self, document_name: str) -> None:
        entries = self.load_entries()
        if document_name in entries:
            del entries[document_name]
            self.save_entries(entries)
