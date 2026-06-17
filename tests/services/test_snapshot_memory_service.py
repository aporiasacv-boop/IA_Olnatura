import json
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from app.domain.analytics_context import AnalyticsContextSnapshot, AnalyticsDateRange, AnalyticsInsights, CustomerConcentration
from app.domain.executive_insights import ExecutiveInsights
from app.models.organizational_snapshot import OrganizationalSnapshot
from app.services.analytics_context_service import AnalyticsContextService
from app.services.memory_insights_service import MemoryInsightsService
from app.services.snapshot_memory_service import SnapshotMemoryService

_SNAPSHOT = AnalyticsContextSnapshot(
    summary={'total_customers': 100, 'total_orders': 100, 'total_sales_amount': '49722777.13', 'average_ticket': '497227.77'},
    sales_by_status=[],
    top_customers=[],
    date_range=AnalyticsDateRange(start_date='2025-01-01', end_date='2025-06-15'),
    insights=AnalyticsInsights(
        largest_customer_share=42.2,
        customer_concentration=CustomerConcentration(top_5_share=72.0, customers_with_sales=25, leading_customer='FARMACIAS DE SIMILARES SA DE CV'),
    ),
    financials={'total_revenue': '49722777.13', 'total_orders': 100},
    executive_insights=ExecutiveInsights(
        top_customer_share=42.2,
        top_5_customer_share=72.0,
        top_product_share=42.1,
        dominant_customer='FARMACIAS DE SIMILARES SA DE CV',
        dominant_product='ARISTOCAPS-RB',
        invoice_rate=100.0,
        revenue_concentration='Concentracion comercial moderada',
        risk_flags=['Concentracion comercial moderada'],
    ),
)


def _build_service() -> tuple[SnapshotMemoryService, MagicMock, MagicMock]:
    repository = MagicMock()
    analytics_context = MagicMock(spec=AnalyticsContextService)
    analytics_context.build_snapshot.return_value = _SNAPSHOT
    service = SnapshotMemoryService(repository, analytics_context, MemoryInsightsService())
    return service, repository, analytics_context


def test_save_snapshot_persists_record() -> None:
    service, repository, _ = _build_service()
    saved_record = OrganizationalSnapshot(
        id=1,
        snapshot_date=date(2025, 6, 15),
        total_customers=100,
        total_orders=100,
        total_revenue=Decimal('49722777.13'),
        top_customer='FARMACIAS DE SIMILARES SA DE CV',
        top_customer_share=Decimal('42.20'),
        top_product='ARISTOCAPS-RB',
        top_product_share=Decimal('42.10'),
        executive_insights_json='{}',
    )
    repository.create.return_value = saved_record
    result = service.save_snapshot(snapshot_date=date(2025, 6, 15))
    repository.create.assert_called_once()
    created = repository.create.call_args.args[0]
    assert created.total_customers == 100
    assert created.top_customer == 'FARMACIAS DE SIMILARES SA DE CV'
    assert result['total_revenue'] == '49722777.13'


def test_latest_and_previous_snapshot() -> None:
    service, repository, _ = _build_service()
    latest = OrganizationalSnapshot(
        id=2,
        snapshot_date=date(2025, 6, 15),
        total_customers=100,
        total_orders=100,
        total_revenue=Decimal('49722777.13'),
        top_customer='FARMACIAS DE SIMILARES SA DE CV',
        top_customer_share=Decimal('42.20'),
        top_product='ARISTOCAPS-RB',
        top_product_share=Decimal('42.10'),
        executive_insights_json=json.dumps({'risk_flags': ['Concentracion comercial moderada']}),
    )
    previous = OrganizationalSnapshot(
        id=1,
        snapshot_date=date(2025, 6, 1),
        total_customers=100,
        total_orders=98,
        total_revenue=Decimal('49000000.00'),
        top_customer='FARMACIAS DE SIMILARES SA DE CV',
        top_customer_share=Decimal('41.00'),
        top_product='ARISTOCAPS-RB',
        top_product_share=Decimal('41.50'),
        executive_insights_json=json.dumps({'risk_flags': ['Concentracion comercial moderada']}),
    )
    repository.get_latest.return_value = latest
    repository.get_previous.return_value = previous
    assert service.latest_snapshot()['id'] == 2
    assert service.previous_snapshot()['id'] == 1


def test_compare_snapshots_returns_memory_insights() -> None:
    service, repository, _ = _build_service()
    latest = OrganizationalSnapshot(
        id=2,
        snapshot_date=date(2025, 6, 15),
        total_customers=100,
        total_orders=100,
        total_revenue=Decimal('49722777.13'),
        top_customer='FARMACIAS DE SIMILARES SA DE CV',
        top_customer_share=Decimal('42.20'),
        top_product='ARISTOCAPS-RB',
        top_product_share=Decimal('42.10'),
        executive_insights_json=json.dumps({'risk_flags': ['Concentracion comercial moderada']}),
    )
    previous = OrganizationalSnapshot(
        id=1,
        snapshot_date=date(2025, 6, 1),
        total_customers=100,
        total_orders=98,
        total_revenue=Decimal('49000000.00'),
        top_customer='FARMACIAS DE SIMILARES SA DE CV',
        top_customer_share=Decimal('41.00'),
        top_product='ARISTOCAPS-RB',
        top_product_share=Decimal('41.50'),
        executive_insights_json=json.dumps({'risk_flags': ['Concentracion comercial moderada']}),
    )
    repository.get_latest.return_value = latest
    repository.get_previous.return_value = previous
    comparison = service.compare_snapshots()
    assert comparison['latest_snapshot']['id'] == 2
    assert comparison['previous_snapshot']['id'] == 1
    insights = comparison['memory_insights']
    assert any('clientes permanece estable' in item.lower() for item in insights['stable_findings'])
    assert any('pedidos' in item.lower() for item in insights['changes'])
