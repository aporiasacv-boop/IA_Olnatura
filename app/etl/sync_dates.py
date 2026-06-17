from datetime import date

from app.core.config import Settings

def parse_sync_date(value: str | None) -> date | None:
    if not value or not value.strip():
        return None
    return date.fromisoformat(value.strip())

def resolve_sync_date_range(settings: Settings) -> tuple[date | None, date | None]:
    return (
        parse_sync_date(settings.SYNC_START_DATE),
        parse_sync_date(settings.SYNC_END_DATE),
    )
