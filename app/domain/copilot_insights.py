from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CopilotInsights:
    observations: list[str]
    attention_points: list[str]
    recommended_reviews: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            'observations': list(self.observations),
            'attention_points': list(self.attention_points),
            'recommended_reviews': list(self.recommended_reviews),
        }
