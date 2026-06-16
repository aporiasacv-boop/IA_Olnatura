from unittest.mock import MagicMock
from app.domain.chat import ChatIntent
from app.services.ai_response_service import AIResponseService
from app.services.business_assistant_service import BusinessAssistantService
from app.services.chat_service import ChatResult, ChatService
from app.services.question_classifier import QuestionClassifier
from app.services.semantic_search_service import SemanticSearchHit, SemanticSearchResult, SemanticSearchService

def test_ask_routes_to_analytics_for_known_intent() -> None:
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question='¿Cuántos clientes tenemos?',
        intent=ChatIntent.CUSTOMERS_COUNT,
        data={'total_customers': 100},
    )
    semantic_search = MagicMock(spec=SemanticSearchService)
    ai_response = MagicMock(spec=AIResponseService)
    ai_response.generate.return_value = 'Actualmente existen 100 clientes sincronizados desde Dynamics 365 Finance & Operations.'
    service = BusinessAssistantService(chat_service, semantic_search, ai_response)
    result = service.ask('¿Cuántos clientes tenemos?')
    assert result.source == 'analytics'
    assert '100 clientes' in result.answer
    ai_response.generate.assert_called_once_with(
        question='¿Cuántos clientes tenemos?',
        intent='customers_count',
        data={'total_customers': 100},
    )
    semantic_search.search.assert_not_called()

def test_ask_routes_to_documents_for_unknown_intent() -> None:
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question='¿Cuál es el objeto social de la empresa?',
        intent=ChatIntent.UNKNOWN,
        data=None,
    )
    semantic_search = MagicMock(spec=SemanticSearchService)
    semantic_search.search.return_value = SemanticSearchResult(
        query='¿Cuál es el objeto social de la empresa?',
        results=[SemanticSearchHit(document='Acta_Constitutiva.docx', score=0.93, content='El objeto social es comercializar productos naturales.')],
    )
    ai_response = MagicMock(spec=AIResponseService)
    ai_response.generate_from_documents.return_value = 'El objeto social de la empresa es comercializar productos naturales.'
    service = BusinessAssistantService(chat_service, semantic_search, ai_response)
    result = service.ask('¿Cuál es el objeto social de la empresa?')
    assert result.source == 'documents'
    assert 'objeto social' in result.answer.lower()
    semantic_search.search.assert_called_once_with('¿Cuál es el objeto social de la empresa?')
    ai_response.generate_from_documents.assert_called_once()

def test_ask_documents_returns_message_when_no_results() -> None:
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question='¿Cuál es el objeto social?',
        intent=ChatIntent.UNKNOWN,
        data=None,
    )
    semantic_search = MagicMock(spec=SemanticSearchService)
    semantic_search.search.return_value = SemanticSearchResult(query='¿Cuál es el objeto social?', results=[])
    ai_response = MagicMock(spec=AIResponseService)
    service = BusinessAssistantService(chat_service, semantic_search, ai_response)
    result = service.ask('¿Cuál es el objeto social?')
    assert result.source == 'documents'
    assert 'No se encontraron fragmentos relevantes' in result.answer
    ai_response.generate_from_documents.assert_not_called()

def test_ask_logs_route_and_timing() -> None:
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question='¿Cuántos pedidos tenemos?',
        intent=ChatIntent.SALES_COUNT,
        data={'total_sales_orders': 5},
    )
    semantic_search = MagicMock(spec=SemanticSearchService)
    ai_response = MagicMock(spec=AIResponseService)
    ai_response.generate.return_value = 'Hay 5 pedidos.'
    logger = MagicMock()
    service = BusinessAssistantService(chat_service, semantic_search, ai_response, logger=logger)
    service.ask('¿Cuántos pedidos tenemos?')
    logger.info.assert_called_once()
    log_message = logger.info.call_args.args[0]
    assert log_message == 'route_selected=%s response_source=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f'
    assert logger.info.call_args.args[1] == 'analytics'
    assert logger.info.call_args.args[2] == 'analytics'
    assert logger.info.call_args.args[3] == 1
    assert logger.info.call_args.args[4] == 0

def test_ask_routes_to_hybrid_when_analytics_and_document_signals() -> None:
    question = '¿Cuántos clientes tenemos y cómo se registran?'
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question=question,
        intent=ChatIntent.CUSTOMERS_COUNT,
        data={'total_customers': 100},
    )
    semantic_search = MagicMock(spec=SemanticSearchService)
    semantic_search.search.return_value = SemanticSearchResult(
        query=question,
        results=[SemanticSearchHit(document='Manual_Clientes.pdf', score=0.88, content='Los clientes se registran en el modulo de ventas.')],
    )
    ai_response = MagicMock(spec=AIResponseService)
    ai_response.generate_hybrid.return_value = 'Hay 100 clientes y se registran en el modulo de ventas.'
    classifier = QuestionClassifier()
    service = BusinessAssistantService(chat_service, semantic_search, ai_response, classifier=classifier)
    result = service.ask(question)
    assert result.source == 'hybrid'
    assert '100 clientes' in result.answer
    semantic_search.search.assert_called_once_with(question)
    ai_response.generate_hybrid.assert_called_once()
    ai_response.generate.assert_not_called()
    fused_context = ai_response.generate_hybrid.call_args.kwargs['context']
    assert fused_context.analytics_intent == 'customers_count'
    assert fused_context.document_hits == 1

def test_ask_hybrid_logs_analytics_and_document_hits() -> None:
    question = '¿Cuál es el ticket promedio y cuál es el procedimiento de ventas?'
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question=question,
        intent=ChatIntent.SALES_AVERAGE_TICKET,
        data={'total_orders': 10, 'total_amount': '1000.00', 'average_order_amount': '100.00'},
    )
    semantic_search = MagicMock(spec=SemanticSearchService)
    semantic_search.search.return_value = SemanticSearchResult(
        query=question,
        results=[
            SemanticSearchHit(document='Procedimiento_Ventas.docx', score=0.91, content='El procedimiento inicia con la cotizacion.'),
            SemanticSearchHit(document='Manual_Ventas.pdf', score=0.85, content='Validar inventario antes de confirmar.'),
        ],
    )
    ai_response = MagicMock(spec=AIResponseService)
    ai_response.generate_hybrid.return_value = 'El ticket promedio es 100 y el procedimiento inicia con la cotizacion.'
    logger = MagicMock()
    classifier = QuestionClassifier()
    service = BusinessAssistantService(chat_service, semantic_search, ai_response, classifier=classifier, logger=logger)
    service.ask(question)
    assert logger.info.call_args.args[1] == 'hybrid'
    assert logger.info.call_args.args[2] == 'hybrid'
    assert logger.info.call_args.args[3] == 1
    assert logger.info.call_args.args[4] == 2

def test_ask_hybrid_with_no_document_results_still_uses_hybrid_path() -> None:
    question = '¿Cuántos pedidos tenemos y cuál es el procedimiento de ventas?'
    chat_service = MagicMock(spec=ChatService)
    chat_service.process.return_value = ChatResult(
        question=question,
        intent=ChatIntent.SALES_COUNT,
        data={'total_sales_orders': 5},
    )
    semantic_search = MagicMock(spec=SemanticSearchService)
    semantic_search.search.return_value = SemanticSearchResult(query=question, results=[])
    ai_response = MagicMock(spec=AIResponseService)
    ai_response.generate_hybrid.return_value = 'Hay 5 pedidos. No hay procedimiento documental disponible.'
    classifier = QuestionClassifier()
    service = BusinessAssistantService(chat_service, semantic_search, ai_response, classifier=classifier)
    result = service.ask(question)
    assert result.source == 'hybrid'
    fused_context = ai_response.generate_hybrid.call_args.kwargs['context']
    assert fused_context.document_hits == 0
    assert fused_context.analytics_hits == 1
