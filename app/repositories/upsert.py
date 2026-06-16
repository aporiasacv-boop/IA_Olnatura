from typing import Any
from sqlalchemy.orm import Session

def bulk_upsert(session: Session, table, records: list[dict[str, Any]], index_elements: list[str]) -> int:
    if not records:
        return 0
    dialect_name = session.get_bind().dialect.name
    if dialect_name == 'postgresql':
        from sqlalchemy.dialects.postgresql import insert as dialect_insert
    else:
        from sqlalchemy.dialects.sqlite import insert as dialect_insert
    stmt = dialect_insert(table).values(records)
    update_columns = {col.name: stmt.excluded[col.name] for col in table.columns if col.name not in index_elements and col.name not in ('id', 'created_at')}
    stmt = stmt.on_conflict_do_update(index_elements=index_elements, set_=update_columns)
    session.execute(stmt)
    return len(records)
