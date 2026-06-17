from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CopilotContext:
    analytics_snapshot: dict[str, Any]
    executive_insights: dict[str, Any]
    hybrid_insights: dict[str, Any]
    copilot_insights: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            'analytics_snapshot': self.analytics_snapshot,
            'executive_insights': self.executive_insights,
            'hybrid_insights': self.hybrid_insights,
            'copilot_insights': self.copilot_insights,
        }
