import json
from datetime import date
from decimal import Decimal
from typing import Any

from app.domain.memory_insights import MemoryInsights
from app.models.organizational_snapshot import OrganizationalSnapshot
from app.repositories.organizational_snapshot_repository import OrganizationalSnapshotRepository
from app.services.analytics_context_service import AnalyticsContextService
from app.services.memory_insights_service import MemoryInsightsService

class SnapshotMemoryService:

    def __init__(
        self,
        repository: OrganizationalSnapshotRepository,
        analytics_context_service: AnalyticsContextService,
        memory_insights_service: MemoryInsightsService | None = None,
    ):
        self._repository = repository
        self._analytics_context = analytics_context_service
        self._memory_insights = memory_insights_service or MemoryInsightsService()

    def save_snapshot(self, snapshot_date: date | None = None) -> dict[str, Any]:
        payload = self._build_snapshot_payload(snapshot_date or date.today())
        record = OrganizationalSnapshot(**payload)
        saved = self._repository.create(record)
        return saved.to_dict()

    def latest_snapshot(self) -> dict[str, Any] | None:
        record = self._repository.get_latest()
        return record.to_dict() if record else None

    def previous_snapshot(self) -> dict[str, Any] | None:
        record = self._repository.get_previous()
        return record.to_dict() if record else None

    def compare_snapshots(self) -> dict[str, Any]:
        latest = self.latest_snapshot()
        previous = self.previous_snapshot()
        if latest is None:
            return {
                'latest_snapshot': None,
                'previous_snapshot': None,
                'memory_insights': MemoryInsights(changes=[], stable_findings=[], new_findings=[]).to_dict(),
            }
        insights = self._memory_insights.build_insights(latest, previous)
        return {
            'latest_snapshot': latest,
            'previous_snapshot': previous,
            'memory_insights': insights.to_dict(),
        }

    def build_memory_context(self) -> dict[str, Any]:
        comparison = self.compare_snapshots()
        return {
            'latest_snapshot': comparison['latest_snapshot'],
            'previous_snapshot': comparison['previous_snapshot'],
            'memory_insights': comparison['memory_insights'],
        }

    def _build_snapshot_payload(self, snapshot_date: date) -> dict[str, Any]:
        snapshot = self._analytics_context.build_snapshot().to_dict()
        summary = snapshot.get('summary', {})
        financials = snapshot.get('financials', {})
        executive = snapshot.get('executive_insights', {})
        return {
            'snapshot_date': snapshot_date,
            'total_customers': int(summary.get('total_customers', 0)),
            'total_orders': int(summary.get('total_orders', 0)),
            'total_revenue': Decimal(str(financials.get('total_revenue', '0'))),
            'top_customer': executive.get('dominant_customer'),
            'top_customer_share': Decimal(str(executive.get('top_customer_share', 0))),
            'top_product': executive.get('dominant_product'),
            'top_product_share': Decimal(str(executive.get('top_product_share', 0))),
            'executive_insights_json': json.dumps(executive, ensure_ascii=False),
        }
