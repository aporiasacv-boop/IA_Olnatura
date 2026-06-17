import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import create_dynamics_client
from app.core.config import settings

client = create_dynamics_client()
for entity in [settings.D365_CLIENTES_ENTITY, settings.D365_VENTAS_ENTITY]:
    count = client.count_entity(entity)
    stats = client.paginate_entity_stats(entity, page_size=100)
    print(entity, 'count', count, 'paginated', stats.total_records, 'pages', stats.pages_traversed)
