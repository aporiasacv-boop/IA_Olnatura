from dataclasses import dataclass, field

@dataclass(frozen=True)
class EntityVolumeDiagnostics:
    entity_name: str
    total_records: int
    odata_count: int | None
    pages_traversed: int
    next_links_found: int
    records_per_page: tuple[int, ...]
    odata_filter: str | None
    filter_valid: bool
    filter_error: str | None
    duration_seconds: float
    count_matches_pagination: bool | None
    possible_page_size_truncation: bool

@dataclass(frozen=True)
class VolumeDiagnosticsReport:
    customers_d365: int
    customers_postgres: int
    sales_d365: int
    sales_postgres: int
    sales_lines_d365: int
    sales_lines_postgres: int
    pagination_working: bool
    filters_working: bool
    duration_seconds: float
    sync_start_date: str | None
    sync_end_date: str | None
    artificial_limits_detected: bool
    artificial_limit_notes: tuple[str, ...]
    entities: dict[str, EntityVolumeDiagnostics] = field(default_factory=dict)

    def to_report_dict(self) -> dict[str, object]:
        return {
            'customers_d365': self.customers_d365,
            'customers_postgres': self.customers_postgres,
            'customers_diff': self.customers_d365 - self.customers_postgres,
            'sales_d365': self.sales_d365,
            'sales_postgres': self.sales_postgres,
            'sales_diff': self.sales_d365 - self.sales_postgres,
            'sales_lines_d365': self.sales_lines_d365,
            'sales_lines_postgres': self.sales_lines_postgres,
            'sales_lines_diff': self.sales_lines_d365 - self.sales_lines_postgres,
            'pagination_working': self.pagination_working,
            'filters_working': self.filters_working,
            'duration_seconds': round(self.duration_seconds, 2),
            'sync_start_date': self.sync_start_date,
            'sync_end_date': self.sync_end_date,
            'artificial_limits_detected': self.artificial_limits_detected,
            'artificial_limit_notes': list(self.artificial_limit_notes),
            'entities': {
                name: {
                    'total_records': diag.total_records,
                    'odata_count': diag.odata_count,
                    'pages_traversed': diag.pages_traversed,
                    'next_links_found': diag.next_links_found,
                    'records_per_page': list(diag.records_per_page),
                    'odata_filter': diag.odata_filter,
                    'filter_valid': diag.filter_valid,
                    'filter_error': diag.filter_error,
                    'duration_seconds': round(diag.duration_seconds, 2),
                    'count_matches_pagination': diag.count_matches_pagination,
                    'possible_page_size_truncation': diag.possible_page_size_truncation,
                }
                for name, diag in self.entities.items()
            },
        }
