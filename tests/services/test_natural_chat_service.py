from unittest.mock import MagicMock
from app.domain.chat import ChatIntent
from app.services.ai_response_service import AIResponseService
from app.services.chat_service import ChatResult, ChatService
from app.services.natural_chat_service import NaturalChatService

def test_process_generates_natural_answer_for_known_intent() -> None:
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question='¿Cuántos clientes tenemos?',
        intent=ChatIntent.CUSTOMERS_COUNT,
        data={'total_customers': 100},
    )
    ai_response_service = MagicMock(spec=AIResponseService)
    ai_response_service.generate.return_value = 'Actualmente existen 100 clientes sincronizados desde Dynamics 365 Finance & Operations.'
    service = NaturalChatService(chat_service, ai_response_service)
    result = service.process('¿Cuántos clientes tenemos?')
    assert result.intent == 'customers_count'
    assert '100 clientes' in result.answer
    ai_response_service.generate.assert_called_once_with(
        question='¿Cuántos clientes tenemos?',
        intent='customers_count',
        data={'total_customers': 100},
    )

def test_process_skips_llm_for_unknown_intent() -> None:
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question='¿Qué es un ERP?',
        intent=ChatIntent.UNKNOWN,
        data=None,
    )
    ai_response_service = MagicMock(spec=AIResponseService)
    service = NaturalChatService(chat_service, ai_response_service)
    result = service.process('¿Qué es un ERP?')
    assert result.intent == 'unknown'
    assert result.answer
    ai_response_service.generate.assert_not_called()

def test_process_strips_llm_response() -> None:
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question='¿Cuántos pedidos tenemos?',
        intent=ChatIntent.SALES_COUNT,
        data={'total_sales_orders': 5},
    )
    ai_response_service = MagicMock(spec=AIResponseService)
    ai_response_service.generate.return_value = '  Hay 5 pedidos sincronizados.  '
    service = NaturalChatService(chat_service, ai_response_service)
    result = service.process('¿Cuántos pedidos tenemos?')
    assert result.answer == 'Hay 5 pedidos sincronizados.'
