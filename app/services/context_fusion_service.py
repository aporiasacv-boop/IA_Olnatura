from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class FusedContext:
    analytics_intent: str
    analytics_data: dict[str, Any] | list[dict[str, Any]] | None
    document_results: list[dict[str, Any]]

    @property
    def analytics_hits(self) -> int:
        return 1 if self.analytics_data is not None else 0

    @property
    def document_hits(self) -> int:
        return len(self.document_results)

class ContextFusionService:

    def fuse(
        self,
        *,
        intent: str,
        analytics_data: dict[str, Any] | list[dict[str, Any]] | None,
        document_results: list[dict[str, Any]],
    ) -> FusedContext:
        return FusedContext(
            analytics_intent=intent,
            analytics_data=analytics_data,
            document_results=document_results,
        )
