from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class HybridContext:
    analytics_snapshot: dict[str, Any]
    executive_insights: dict[str, Any]
    document_context: dict[str, Any]
    document_insights: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            'analytics_snapshot': self.analytics_snapshot,
            'executive_insights': self.executive_insights,
            'document_context': self.document_context,
            'document_insights': self.document_insights,
        }
