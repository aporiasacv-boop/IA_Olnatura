from decimal import Decimal
from unittest.mock import MagicMock
from app.domain.analytics import SalesSummary, TopCustomer
from app.domain.chat import ChatIntent
from app.services.analytics_service import AnalyticsService
from app.services.chat_service import ChatService
from app.services.question_classifier import QuestionClassifier

def test_process_customers_count() -> None:
    analytics = MagicMock(spec=AnalyticsService)
    analytics.count_clientes.return_value = 230
    service = ChatService(analytics)
    result = service.process('¿Cuántos clientes tenemos?')
    assert result.intent is ChatIntent.CUSTOMERS_COUNT
    assert result.data == {'total_customers': 230}
    analytics.count_clientes.assert_called_once()

def test_process_sales_count() -> None:
    analytics = MagicMock(spec=AnalyticsService)
    analytics.count_sales_orders.return_value = 5678
    service = ChatService(analytics)
    result = service.process('¿Cuántos pedidos tenemos?')
    assert result.intent is ChatIntent.SALES_COUNT
    assert result.data == {'total_sales_orders': 5678}

def test_process_sales_total_amount() -> None:
    analytics = MagicMock(spec=AnalyticsService)
    analytics.sales_summary.return_value = SalesSummary(total_orders=5, total_amount=Decimal('5500.00'), average_order_amount=Decimal('1100.00'))
    service = ChatService(analytics)
    result = service.process('¿Cuál es el monto total vendido?')
    assert result.intent is ChatIntent.SALES_TOTAL_AMOUNT
    assert result.data['total_amount'] == '5500.00'

def test_process_average_ticket() -> None:
    analytics = MagicMock(spec=AnalyticsService)
    analytics.sales_summary.return_value = SalesSummary(total_orders=5, total_amount=Decimal('5500.00'), average_order_amount=Decimal('1100.00'))
    service = ChatService(analytics)
    result = service.process('¿Cuál es el ticket promedio?')
    assert result.intent is ChatIntent.SALES_AVERAGE_TICKET
    assert result.data['average_order_amount'] == '1100.00'

def test_process_top_customers() -> None:
    analytics = MagicMock(spec=AnalyticsService)
    analytics.top_customers.return_value = [TopCustomer('C002', 'Beta SA', 2, Decimal('3800.00'))]
    service = ChatService(analytics, top_customers_limit=5)
    result = service.process('¿Quiénes son nuestros principales clientes?')
    assert result.intent is ChatIntent.TOP_CUSTOMERS
    assert result.data[0]['customer_name'] == 'Beta SA'
    analytics.top_customers.assert_called_once_with(limit=5)

def test_process_unknown_intent() -> None:
    analytics = MagicMock(spec=AnalyticsService)
    service = ChatService(analytics)
    result = service.process('¿Qué es un ERP?')
    assert result.intent is ChatIntent.UNKNOWN
    assert result.data is None
    analytics.count_clientes.assert_not_called()

def test_process_uses_injected_classifier() -> None:
    analytics = MagicMock(spec=AnalyticsService)
    classifier = MagicMock(spec=QuestionClassifier)
    classifier.resolve_intent.return_value = ChatIntent.UNKNOWN
    service = ChatService(analytics, classifier=classifier)
    result = service.process('cualquier pregunta')
    assert result.intent is ChatIntent.UNKNOWN
    classifier.resolve_intent.assert_called_once_with('cualquier pregunta')
