from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class DocumentContext:
    documents: list[dict[str, Any]]
    sources: list[str]
    top_document: str | None
    total_matches: int
    average_score: float
    context: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'documents': self.documents,
            'sources': self.sources,
            'top_document': self.top_document,
            'total_matches': self.total_matches,
            'average_score': self.average_score,
            'context': self.context,
        }
