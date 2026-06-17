from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

@dataclass(frozen=True)
class DocumentMetadataEntry:
    file_hash: str
    document_name: str
    document_type: str
    file_extension: str
    indexed_at: str
    chunk_count: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            'file_hash': self.file_hash,
            'document_name': self.document_name,
            'document_type': self.document_type,
            'file_extension': self.file_extension,
            'indexed_at': self.indexed_at,
            'chunk_count': self.chunk_count,
        }

    @classmethod
    def from_dict(cls, document_name: str, data: dict[str, object]) -> 'DocumentMetadataEntry':
        return cls(
            file_hash=str(data.get('file_hash', '')),
            document_name=str(data.get('document_name', document_name)),
            document_type=str(data.get('document_type', infer_document_type(document_name))),
            file_extension=str(data.get('file_extension', Path(document_name).suffix.lower())),
            indexed_at=str(data.get('indexed_at', datetime.now(timezone.utc).isoformat())),
            chunk_count=int(data.get('chunk_count', 0)),
        )

    @classmethod
    def from_legacy_hash(cls, document_name: str, file_hash: str) -> 'DocumentMetadataEntry':
        return cls(
            file_hash=file_hash,
            document_name=document_name,
            document_type=infer_document_type(document_name),
            file_extension=Path(document_name).suffix.lower(),
            indexed_at=datetime.now(timezone.utc).isoformat(),
            chunk_count=0,
        )

def infer_document_type(document_name: str) -> str:
    lowered = document_name.lower()
    if 'acta' in lowered:
        return 'acta'
    if 'manual' in lowered:
        return 'manual'
    if 'procedimiento' in lowered or 'proceso' in lowered:
        return 'procedimiento'
    if 'politica' in lowered:
        return 'politica'
    return 'documento'

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
