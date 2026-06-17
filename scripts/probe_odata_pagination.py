import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.deps import create_dynamics_client
from app.core.config import settings

ENTITY = settings.D365_CLIENTES_ENTITY

def _probe(client, label: str, *, params: dict | None, prefer: str | None) -> dict:
    url = f"{client._config.base_url.rstrip('/')}/{ENTITY}"
    token = client._oauth_provider.get_access_token()
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    if prefer:
        headers['Prefer'] = prefer
    response = client._http_client.get(url, headers=headers, params=params, timeout=120.0)
    data = response.json() if response.status_code == 200 else {}
    return {
        'label': label,
        'status': response.status_code,
        'value_count': len(data.get('value', [])),
        'has_next_link': '@odata.nextLink' in data,
        'next_link_preview': (data.get('@odata.nextLink') or '')[:120] or None,
        'preference_applied': response.headers.get('preference-applied'),
        'params': params,
        'prefer': prefer,
    }

def main() -> int:
    client = create_dynamics_client()
    probes = [
        ('$top=100', {'$top': 100}, None),
        ('Prefer maxpagesize=100', None, 'odata.maxpagesize=100'),
        ('Prefer maxpagesize=100 + orderby RecId', {'$orderby': 'RecId'}, 'odata.maxpagesize=100'),
        ('$top=100 skip=100', {'$top': 100, '$skip': 100}, None),
        ('$top=100 skip=100 orderby RecId', {'$top': 100, '$skip': 100, '$orderby': 'RecId'}, None),
        ('$top=63 skip=100 orderby RecId', {'$top': 63, '$skip': 100, '$orderby': 'RecId'}, None),
    ]
    results = [_probe(client, label, params=params, prefer=prefer) for label, params, prefer in probes]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
