from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class MemoryInsights:
    changes: list[str]
    stable_findings: list[str]
    new_findings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            'changes': list(self.changes),
            'stable_findings': list(self.stable_findings),
            'new_findings': list(self.new_findings),
        }
