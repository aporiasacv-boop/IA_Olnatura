from __future__ import annotations
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
import httpx
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / '.env'
REQUEST_TIMEOUT = 30.0
CUSTOMERS_PATH = '/CustomersV3?$top=1'

@dataclass(frozen=True)
class AzureCredentials:
    tenant_id: str
    client_id: str
    client_secret: str

@dataclass(frozen=True)
class TokenResult:
    access_token: str
    expires_in: int
    expires_at: datetime

class DynamicsConnectionTestError(Exception):

    def __init__(self, category: str, message: str, detail: str | None=None):
        self.category = category
        self.message = message
        self.detail = detail
        super().__init__(message)

def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and (value[0] in ("'", '"')):
        return value[1:-1]
    return value

def load_flat_env(env_path: Path) -> None:
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if line == 'azure:' or line.startswith('azure:'):
            continue
        if raw_line.startswith((' ', '\t')):
            continue
        if '=' not in line:
            continue
        key, _, value = line.partition('=')
        os.environ.setdefault(key.strip(), value.strip())

def parse_azure_block_from_env(env_path: Path) -> AzureCredentials | None:
    if not env_path.is_file():
        return None
    content = env_path.read_text(encoding='utf-8')
    match = re.search('^azure:\\s*\\n[ \\t]+tenant-id:\\s*[\'\\"]([^\'\\"]+)[\'\\"]\\s*\\n[ \\t]+client-id:\\s*[\'\\"]([^\'\\"]+)[\'\\"]\\s*\\n[ \\t]+client-secret:\\s*[\'\\"]([^\'\\"]+)[\'\\"]', content, flags=re.MULTILINE)
    if not match:
        return None
    return AzureCredentials(tenant_id=match.group(1).strip(), client_id=match.group(2).strip(), client_secret=match.group(3).strip())

def load_credentials() -> AzureCredentials:
    load_flat_env(ENV_FILE)
    azure_block = parse_azure_block_from_env(ENV_FILE)
    if azure_block and all([azure_block.tenant_id, azure_block.client_id, azure_block.client_secret]):
        return azure_block
    tenant_id = os.getenv('AZURE_TENANT_ID') or os.getenv('D365_TENANT_ID', '')
    client_id = os.getenv('AZURE_CLIENT_ID') or os.getenv('D365_CLIENT_ID', '')
    client_secret = os.getenv('AZURE_CLIENT_SECRET') or os.getenv('D365_CLIENT_SECRET', '')
    if not tenant_id or not client_id or (not client_secret):
        raise DynamicsConnectionTestError(category='configuracion', message='Credenciales Azure incompletas en .env', detail='Defina el bloque azure: (tenant-id, client-id, client-secret) o las variables D365_TENANT_ID, D365_CLIENT_ID, D365_CLIENT_SECRET.')
    if tenant_id.startswith('your-') or client_id.startswith('your-'):
        raise DynamicsConnectionTestError(category='configuracion', message='Credenciales Azure con valores placeholder', detail='Actualice .env con tenant-id, client-id y client-secret reales.')
    return AzureCredentials(tenant_id=tenant_id.strip(), client_id=client_id.strip(), client_secret=client_secret.strip())

def load_d365_base_url() -> str:
    load_flat_env(ENV_FILE)
    base_url = os.getenv('D365_BASE_URL', '').strip().rstrip('/')
    if not base_url or 'your-env' in base_url:
        raise DynamicsConnectionTestError(category='configuracion', message='D365_BASE_URL no configurada en .env', detail='Ejemplo: D365_BASE_URL=https://mi-entorno.operations.dynamics.com/data')
    return base_url

def build_oauth_scope(base_url: str) -> str:
    resource_url = base_url.removesuffix('/data').rstrip('/')
    return f'{resource_url}/.default'

def classify_oauth_error(status_code: int, response_text: str) -> DynamicsConnectionTestError:
    text_lower = response_text.lower()
    if status_code in (0,) or 'failed to resolve' in text_lower or 'connection' in text_lower:
        return DynamicsConnectionTestError(category='red', message='Error de red al contactar Azure AD', detail=response_text[:500])
    if 'aadsts90002' in text_lower or ('tenant' in text_lower and 'not found' in text_lower):
        return DynamicsConnectionTestError(category='tenant_incorrecto', message='Tenant incorrecto o no encontrado', detail=_extract_aad_error(response_text))
    if 'aadsts700016' in text_lower or ('application' in text_lower and 'not found' in text_lower):
        return DynamicsConnectionTestError(category='client_id_incorrecto', message='Client ID incorrecto o aplicación no registrada en el tenant', detail=_extract_aad_error(response_text))
    if 'aadsts7000215' in text_lower or 'invalid_client' in text_lower or 'client secret' in text_lower or ('invalid_client_secret' in text_lower):
        return DynamicsConnectionTestError(category='secret_incorrecto', message='Client Secret incorrecto o expirado', detail=_extract_aad_error(response_text))
    if status_code == 401:
        return DynamicsConnectionTestError(category='autenticacion', message='Error de autenticación OAuth (401)', detail=_extract_aad_error(response_text))
    return DynamicsConnectionTestError(category='oauth', message=f'Error OAuth HTTP {status_code}', detail=_extract_aad_error(response_text))

def _extract_aad_error(response_text: str) -> str:
    try:
        data = json.loads(response_text)
        parts = [data.get('error'), data.get('error_description')]
        return ' — '.join((part for part in parts if part)) or response_text[:500]
    except json.JSONDecodeError:
        return response_text[:500]

def request_oauth_token(credentials: AzureCredentials, scope: str) -> TokenResult:
    token_url = f'https://login.microsoftonline.com/{credentials.tenant_id}/oauth2/v2.0/token'
    payload = {'grant_type': 'client_credentials', 'client_id': credentials.client_id, 'client_secret': credentials.client_secret, 'scope': scope}
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(token_url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    except httpx.TimeoutException as exc:
        raise DynamicsConnectionTestError(category='red', message='Timeout al solicitar token OAuth', detail=str(exc)) from exc
    except httpx.RequestError as exc:
        raise DynamicsConnectionTestError(category='red', message='Error de red al solicitar token OAuth', detail=str(exc)) from exc
    if response.status_code != 200:
        raise classify_oauth_error(response.status_code, response.text)
    data = response.json()
    access_token = data.get('access_token')
    if not access_token:
        raise DynamicsConnectionTestError(category='oauth', message='La respuesta OAuth no incluye access_token', detail=response.text[:500])
    expires_in = int(data.get('expires_in', 0))
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
    return TokenResult(access_token=access_token, expires_in=expires_in, expires_at=expires_at)

def classify_odata_error(status_code: int, response_text: str) -> DynamicsConnectionTestError:
    text_lower = response_text.lower()
    if status_code == 403 or 'forbidden' in text_lower or 'authorization' in text_lower:
        return DynamicsConnectionTestError(category='permisos_insuficientes', message='Permisos insuficientes para acceder a CustomersV3', detail=response_text[:500])
    if status_code == 401:
        return DynamicsConnectionTestError(category='autenticacion', message='Token rechazado por Dynamics (401)', detail=response_text[:500])
    if status_code == 404:
        return DynamicsConnectionTestError(category='odata', message='Entidad CustomersV3 no encontrada (404)', detail='Verifique D365_BASE_URL y que la entidad exista en el entorno.')
    return DynamicsConnectionTestError(category='odata', message=f'Error OData HTTP {status_code}', detail=response_text[:500])

def query_customers_v3(base_url: str, access_token: str) -> tuple[int, int]:
    url = f"{base_url.rstrip('/')}{CUSTOMERS_PATH}"
    headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise DynamicsConnectionTestError(category='red', message='Timeout al consultar CustomersV3', detail=str(exc)) from exc
    except httpx.RequestError as exc:
        raise DynamicsConnectionTestError(category='red', message='Error de red al consultar CustomersV3', detail=str(exc)) from exc
    if response.status_code != 200:
        raise classify_odata_error(response.status_code, response.text)
    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise DynamicsConnectionTestError(category='odata', message='Respuesta OData no es JSON válido', detail=response.text[:500]) from exc
    records = data.get('value', [])
    if not isinstance(records, list):
        records = []
    return (response.status_code, len(records))

def _mask_secret(secret: str) -> str:
    if len(secret) <= 4:
        return '****'
    return f'{secret[:2]}...{secret[-2:]}'

def print_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(title)
    print('=' * 60)

def main() -> int:
    print_header('Validación OAuth — Dynamics 365 Finance & Operations')
    print(f'Proyecto: {PROJECT_ROOT}')
    print(f'Archivo .env: {ENV_FILE}')
    try:
        credentials = load_credentials()
        base_url = load_d365_base_url()
        scope = build_oauth_scope(base_url)
        print_header('1. Credenciales cargadas desde .env')
        print(f'  Tenant ID:   {credentials.tenant_id}')
        print(f'  Client ID:   {credentials.client_id}')
        print(f'  Secret:      {_mask_secret(credentials.client_secret)}')
        print(f'  D365 URL:    {base_url}')
        print(f'  OAuth Scope: {scope}')
        print_header('2. Solicitud de token OAuth (Client Credentials)')
        token_result = request_oauth_token(credentials, scope)
        print('  [OK] Token obtenido correctamente')
        print(f'  Expira en:   {token_result.expires_in} segundos')
        print(f"  Expira a las: {token_result.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f'  Token (preview): {token_result.access_token[:20]}...')
        print_header('3. Consulta OData CustomersV3?$top=1')
        http_status, record_count = query_customers_v3(base_url, token_result.access_token)
        print(f'  HTTP Status:           {http_status}')
        print(f'  Registros devueltos:   {record_count}')
        print_header('RESULTADO')
        print('  [OK] Conectividad OAuth y OData validada correctamente.')
        return 0
    except DynamicsConnectionTestError as exc:
        print_header('ERROR')
        print(f'  Categoría: {exc.category}')
        print(f'  Mensaje:   {exc.message}')
        if exc.detail:
            print(f'  Detalle:   {exc.detail}')
        return 1
    except Exception as exc:
        print_header('ERROR INESPERADO')
        print(f'  {type(exc).__name__}: {exc}')
        return 2
if __name__ == '__main__':
    sys.exit(main())
