from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class DocumentInsights:
    total_matches: int
    confidence_level: str
    top_document: str | None
    source_documents: list[str]
    average_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            'total_matches': self.total_matches,
            'confidence_level': self.confidence_level,
            'top_document': self.top_document,
            'source_documents': list(self.source_documents),
            'average_score': self.average_score,
        }
