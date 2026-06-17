from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.deps import get_snapshot_memory_service
from app.main import app


def test_post_memory_snapshot_success() -> None:
    mock_service = MagicMock()
    mock_service.save_snapshot.return_value = {
        'id': 1,
        'snapshot_date': '2025-06-15',
        'total_customers': 100,
        'total_orders': 100,
        'total_revenue': '49722777.13',
        'top_customer': 'FARMACIAS DE SIMILARES SA DE CV',
        'top_customer_share': 42.2,
        'top_product': 'ARISTOCAPS-RB',
        'top_product_share': 42.1,
        'created_at': '2025-06-15T10:00:00',
    }
    app.dependency_overrides[get_snapshot_memory_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/memory/snapshot')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['snapshot']['total_customers'] == 100
    assert data['snapshot']['top_customer'] == 'FARMACIAS DE SIMILARES SA DE CV'
    mock_service.save_snapshot.assert_called_once()


def test_get_memory_latest_success() -> None:
    mock_service = MagicMock()
    mock_service.latest_snapshot.return_value = {
        'id': 1,
        'snapshot_date': '2025-06-15',
        'total_customers': 100,
        'total_orders': 100,
        'total_revenue': '49722777.13',
        'top_customer': 'FARMACIAS DE SIMILARES SA DE CV',
        'top_customer_share': 42.2,
        'top_product': 'ARISTOCAPS-RB',
        'top_product_share': 42.1,
        'created_at': '2025-06-15T10:00:00',
    }
    app.dependency_overrides[get_snapshot_memory_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/memory/latest')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()['total_revenue'] == '49722777.13'


def test_get_memory_latest_returns_404_when_empty() -> None:
    mock_service = MagicMock()
    mock_service.latest_snapshot.return_value = None
    app.dependency_overrides[get_snapshot_memory_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/memory/latest')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404


def test_get_memory_compare_success() -> None:
    snapshot = {
        'id': 2,
        'snapshot_date': '2025-06-15',
        'total_customers': 100,
        'total_orders': 100,
        'total_revenue': '49722777.13',
        'top_customer': 'FARMACIAS DE SIMILARES SA DE CV',
        'top_customer_share': 42.2,
        'top_product': 'ARISTOCAPS-RB',
        'top_product_share': 42.1,
        'created_at': '2025-06-15T10:00:00',
    }
    mock_service = MagicMock()
    mock_service.compare_snapshots.return_value = {
        'latest_snapshot': snapshot,
        'previous_snapshot': dict(snapshot, id=1, snapshot_date='2025-06-01', total_orders=98),
        'memory_insights': {
            'changes': ['Pedidos: 98 -> 100'],
            'stable_findings': ['El numero de clientes permanece estable'],
            'new_findings': [],
        },
    }
    app.dependency_overrides[get_snapshot_memory_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.get('/memory/compare')
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data['memory_insights']['changes'][0] == 'Pedidos: 98 -> 100'
    assert data['previous_snapshot']['total_orders'] == 98
