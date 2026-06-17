from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class HybridInsights:
    cross_source_findings: list[str]
    related_documents: list[str]
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'cross_source_findings': list(self.cross_source_findings),
            'related_documents': list(self.related_documents),
            'confidence': self.confidence,
        }
