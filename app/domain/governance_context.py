from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class GovernanceContext:
    source_type: str
    source_tables: list[str]
    source_documents: list[str]
    confidence_level: str
    snapshot_date: str | None
    records_analyzed: int
    evidence: list[dict[str, Any]]
    generated_at: str
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'source_type': self.source_type,
            'source_tables': list(self.source_tables),
            'source_documents': list(self.source_documents),
            'confidence_level': self.confidence_level,
            'snapshot_date': self.snapshot_date,
            'records_analyzed': self.records_analyzed,
            'evidence': list(self.evidence),
            'generated_at': self.generated_at,
            'limitations': list(self.limitations),
        }

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
