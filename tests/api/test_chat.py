from collections.abc import Generator
from decimal import Decimal
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.api.deps import get_chat_service, get_db
from app.domain.chat import ChatIntent
from app.main import app
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService
from app.services.chat_service import ChatResult, ChatService

@pytest.fixture
def chat_client(analytics_db: Session) -> Generator[TestClient, None, None]:

    def override_get_db() -> Generator[Session, None, None]:
        yield analytics_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_post_chat_customers_count(chat_client: TestClient) -> None:
    response = chat_client.post('/chat', json={'question': '¿Cuántos clientes tenemos?'})
    assert response.status_code == 200
    data = response.json()
    assert data['question'] == '¿Cuántos clientes tenemos?'
    assert data['intent'] == 'customers_count'
    assert data['data'] == {'total_customers': 3}

def test_post_chat_sales_count(chat_client: TestClient) -> None:
    response = chat_client.post('/chat', json={'question': '¿Cuántos pedidos tenemos?'})
    assert response.status_code == 200
    data = response.json()
    assert data['intent'] == 'sales_count'
    assert data['data'] == {'total_sales_orders': 5}

def test_post_chat_sales_summary(chat_client: TestClient) -> None:
    response = chat_client.post('/chat', json={'question': '¿Cuál es el monto total vendido?'})
    assert response.status_code == 200
    data = response.json()
    assert data['intent'] == 'sales_total_amount'
    assert data['data']['total_orders'] == 5
    assert Decimal(data['data']['total_amount']) == Decimal('5500.00')

def test_post_chat_average_ticket(chat_client: TestClient) -> None:
    response = chat_client.post('/chat', json={'question': '¿Cuál es el ticket promedio?'})
    assert response.status_code == 200
    data = response.json()
    assert data['intent'] == 'sales_average_ticket'
    assert Decimal(data['data']['average_order_amount']) == Decimal('1100.00')

def test_post_chat_top_customers(chat_client: TestClient) -> None:
    response = chat_client.post('/chat', json={'question': '¿Quiénes son nuestros principales clientes?'})
    assert response.status_code == 200
    data = response.json()
    assert data['intent'] == 'top_customers'
    assert len(data['data']) == 3
    assert data['data'][0]['customer_account'] == 'C002'

def test_post_chat_unknown_intent(chat_client: TestClient) -> None:
    response = chat_client.post('/chat', json={'question': '¿Qué es un ERP?'})
    assert response.status_code == 200
    data = response.json()
    assert data['intent'] == 'unknown'
    assert data['data'] is None

def test_post_chat_validates_empty_question() -> None:
    with TestClient(app) as client:
        response = client.post('/chat', json={'question': ''})
    assert response.status_code == 422

def test_post_chat_with_mocked_service() -> None:
    mock_service = MagicMock(spec=ChatService)
    mock_service.process.return_value = ChatResult(question='¿Cuántos clientes tenemos?', intent=ChatIntent.CUSTOMERS_COUNT, data={'total_customers': 1})
    app.dependency_overrides[get_chat_service] = lambda: mock_service
    try:
        with TestClient(app) as client:
            response = client.post('/chat', json={'question': '¿Cuántos clientes tenemos?'})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    mock_service.process.assert_called_once_with('¿Cuántos clientes tenemos?')
