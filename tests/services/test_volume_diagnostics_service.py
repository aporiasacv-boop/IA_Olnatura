from unittest.mock import MagicMock

from app.core.config import Settings
from app.integrations.dynamics.odata_client import EntityPaginationStats
from app.services.volume_diagnostics_service import VolumeDiagnosticsService, explain_hundred_records
from app.domain.volume_diagnostics import VolumeDiagnosticsReport, EntityVolumeDiagnostics

def test_detect_artificial_limits_flags_legacy_env(monkeypatch) -> None:
    monkeypatch.setenv('SYNC_VENTAS_MAX_RECORDS', '100')
    service = VolumeDiagnosticsService(db=MagicMock(), dynamics_client=MagicMock())
    notes = service._detect_artificial_limits()
    assert any('SYNC_VENTAS_MAX_RECORDS' in note for note in notes)

def test_detect_possible_truncation_when_count_differs() -> None:
    assert VolumeDiagnosticsService._detect_possible_truncation(
        total_records=100,
        pages_traversed=1,
        records_per_page=(100,),
        odata_count=250,
        page_size=100,
    ) is True

def test_detect_possible_truncation_when_counts_match() -> None:
    assert VolumeDiagnosticsService._detect_possible_truncation(
        total_records=100,
        pages_traversed=1,
        records_per_page=(100,),
        odata_count=100,
        page_size=100,
    ) is False

def test_explain_hundred_records_mentions_mvp_history() -> None:
    report = VolumeDiagnosticsReport(
        customers_d365=100,
        customers_postgres=100,
        sales_d365=100,
        sales_postgres=100,
        sales_lines_d365=100,
        sales_lines_postgres=100,
        pagination_working=True,
        filters_working=True,
        duration_seconds=1.0,
        sync_start_date=None,
        sync_end_date=None,
        artificial_limits_detected=True,
        artificial_limit_notes=('SYNC_VENTAS_MAX_RECORDS=100 presente en entorno',),
        entities={
            'CustomersV3': EntityVolumeDiagnostics(
                entity_name='CustomersV3',
                total_records=100,
                odata_count=100,
                pages_traversed=1,
                next_links_found=0,
                records_per_page=(100,),
                odata_filter=None,
                filter_valid=True,
                filter_error=None,
                duration_seconds=0.5,
                count_matches_pagination=True,
                possible_page_size_truncation=False,
            ),
        },
    )
    explanation = explain_hundred_records(report)
    assert '100' in explanation
    assert 'MVP' in explanation or 'SYNC_' in explanation

def test_run_builds_report_from_client(monkeypatch) -> None:
    client = MagicMock()
    client.validate_filter.return_value = (True, None)
    client.count_entity.return_value = 2
    client.paginate_entity_stats.return_value = EntityPaginationStats(
        total_records=2,
        pages_traversed=1,
        next_links_found=0,
        records_per_page=(2,),
        duration_seconds=0.1,
        last_page_had_next_link=False,
    )
    db = MagicMock()
    repo_patch = monkeypatch.setattr
    from app.services import volume_diagnostics_service as module
    repo_patch(module, 'ClienteRepository', lambda _db: type('R', (), {'count': lambda self: 2})())
    repo_patch(module, 'VentaRepository', lambda _db: type('R', (), {'count': lambda self: 2})())
    repo_patch(module, 'VentaLineaRepository', lambda _db: type('R', (), {'count': lambda self: 2})())
    service = VolumeDiagnosticsService(db=db, dynamics_client=client, app_settings=Settings())
    report = service.run()
    assert report.customers_d365 == 2
    assert report.customers_postgres == 2
    assert report.pagination_working is True
