from unittest.mock import MagicMock

from app.domain.analytics_context import AnalyticsContextSnapshot, AnalyticsDateRange, AnalyticsInsights, CustomerConcentration
from app.domain.executive_insights import ExecutiveInsights

from app.domain.chat import ChatIntent

from app.services.ai_response_service import AIResponseService

from app.services.analytics_context_service import AnalyticsContextService

from app.services.business_assistant_service import BusinessAssistantService

from app.services.chat_service import ChatResult, ChatService

from app.services.question_classifier import QuestionClassifier

from app.services.semantic_search_service import SemanticSearchHit, SemanticSearchResult, SemanticSearchService



_SNAPSHOT = AnalyticsContextSnapshot(

    summary={

        'total_customers': 100,

        'total_orders': 100,

        'total_sales_amount': '2500000.00',

        'average_ticket': '25000.00',

    },

    sales_by_status=[{'status': 'Open', 'count': 40}],

    top_customers=[{'customer_account': 'C001', 'customer_name': 'Alpha', 'orders': 10, 'total_amount': '1050000.00'}],

    date_range=AnalyticsDateRange(start_date='2025-01-01', end_date='2025-06-30'),

    insights=AnalyticsInsights(

        largest_customer_share=42.5,

        customer_concentration=CustomerConcentration(top_5_share=72.0, customers_with_sales=25, leading_customer='Alpha'),

    ),

    financials={

        'total_revenue': '2500000.00',

        'average_order_value': '25000.00',

        'total_lines': 250,

        'total_orders': 100,

        'top_customers_by_revenue': [{'customer_account': 'C001', 'customer_name': 'Alpha', 'lines': 50, 'total_revenue': '1050000.00'}],

        'top_products': [{'product_number': 'P1', 'product_name': 'Producto A', 'lines': 30, 'total_revenue': '800000.00'}],

        'sales_by_status': [{'status': 'Invoiced', 'count': 200, 'total_revenue': '2400000.00'}],

    },

    executive_insights=ExecutiveInsights(
        top_customer_share=42.0,
        top_5_customer_share=72.0,
        top_product_share=32.0,
        dominant_customer='Alpha',
        dominant_product='Producto A',
        invoice_rate=100.0,
        revenue_concentration='Concentracion comercial moderada',
        risk_flags=['Concentracion comercial moderada'],
    ),

)



def _build_service(

    chat_service: MagicMock,

    semantic_search: MagicMock,

    ai_response: MagicMock,

    analytics_context: MagicMock | None = None,

    classifier: QuestionClassifier | None = None,

) -> BusinessAssistantService:

    analytics_context = analytics_context or MagicMock(spec=AnalyticsContextService)

    analytics_context.build_snapshot.return_value = _SNAPSHOT

    return BusinessAssistantService(

        chat_service=chat_service,

        semantic_search_service=semantic_search,

        ai_response_service=ai_response,

        analytics_context_service=analytics_context,

        classifier=classifier or QuestionClassifier(),

    )



def test_ask_routes_to_analytics_with_full_snapshot() -> None:

    chat_service = MagicMock(spec=ChatService)

    chat_service.process.return_value = ChatResult(

        question='¿Cuántos clientes tenemos?',

        intent=ChatIntent.CUSTOMERS_COUNT,

        data={'total_customers': 100},

    )

    semantic_search = MagicMock(spec=SemanticSearchService)

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_business_analysis.return_value = 'La cartera cuenta con 100 clientes activos y un volumen comercial relevante.'

    analytics_context = MagicMock(spec=AnalyticsContextService)

    analytics_context.build_snapshot.return_value = _SNAPSHOT

    service = _build_service(chat_service, semantic_search, ai_response, analytics_context)

    result = service.ask('¿Cuántos clientes tenemos?')

    assert result.source == 'analytics'

    ai_response.generate_business_analysis.assert_called_once()

    call_kwargs = ai_response.generate_business_analysis.call_args.kwargs

    assert call_kwargs['question'] == '¿Cuántos clientes tenemos?'

    assert call_kwargs['snapshot']['summary']['total_customers'] == 100

    assert call_kwargs['snapshot']['insights']['largest_customer_share'] == 42.5

    ai_response.generate.assert_not_called()

    semantic_search.search.assert_not_called()



def test_ask_routes_executive_question_to_executive_summary() -> None:

    chat_service = MagicMock(spec=ChatService)

    chat_service.process.return_value = ChatResult(

        question='Dame un resumen ejecutivo de ventas',

        intent=ChatIntent.UNKNOWN,

        data=None,

    )

    semantic_search = MagicMock(spec=SemanticSearchService)

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_executive_summary.return_value = 'Resumen ejecutivo generado.'

    service = _build_service(chat_service, semantic_search, ai_response)

    result = service.ask('Dame un resumen ejecutivo de ventas')

    assert result.source == 'executive'

    ai_response.generate_executive_summary.assert_called_once()

    ai_response.generate_business_analysis.assert_not_called()



def test_ask_executive_logs_executive_mode() -> None:

    chat_service = MagicMock(spec=ChatService)

    chat_service.process.return_value = ChatResult(

        question='¿Hay riesgos comerciales?',

        intent=ChatIntent.UNKNOWN,

        data=None,

    )

    semantic_search = MagicMock(spec=SemanticSearchService)

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_executive_summary.return_value = 'Se observan riesgos de concentracion.'

    logger = MagicMock()

    service = _build_service(chat_service, semantic_search, ai_response)

    service._logger = logger

    result = service.ask('¿Hay riesgos comerciales?')

    assert result.source == 'executive'

    logger.info.assert_called_once()

    assert logger.info.call_args.args[1] == 'executive'

    assert logger.info.call_args.args[3] is True



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

    semantic_search.get_metadata_entries.return_value = {}

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_document_analysis.return_value = 'El objeto social de la empresa es comercializar productos naturales.'

    service = _build_service(chat_service, semantic_search, ai_response)

    result = service.ask('¿Cuál es el objeto social de la empresa?')

    assert result.source == 'documents'

    semantic_search.search.assert_called_once_with('¿Cuál es el objeto social de la empresa?', top_k=None)

    ai_response.generate_document_analysis.assert_called_once()



def test_ask_documents_returns_message_when_no_results() -> None:

    chat_service = MagicMock(spec=ChatService)

    chat_service.process.return_value = ChatResult(

        question='¿Cuál es el objeto social?',

        intent=ChatIntent.UNKNOWN,

        data=None,

    )

    semantic_search = MagicMock(spec=SemanticSearchService)

    semantic_search.search.return_value = SemanticSearchResult(query='¿Cuál es el objeto social?', results=[])

    semantic_search.get_metadata_entries.return_value = {}

    ai_response = MagicMock(spec=AIResponseService)

    service = _build_service(chat_service, semantic_search, ai_response)

    result = service.ask('¿Cuál es el objeto social?')

    assert result.source == 'documents'

    assert 'No se encontraron fragmentos relevantes' in result.answer

    ai_response.generate_document_analysis.assert_not_called()



def test_ask_documents_logs_document_mode() -> None:

    chat_service = MagicMock(spec=ChatService)

    chat_service.process.return_value = ChatResult(

        question='¿Qué hace el analista de procesos?',

        intent=ChatIntent.UNKNOWN,

        data=None,

    )

    semantic_search = MagicMock(spec=SemanticSearchService)

    semantic_search.search.return_value = SemanticSearchResult(

        query='¿Qué hace el analista de procesos?',

        results=[SemanticSearchHit(document='Manual_Analista_Procesos.pdf', score=0.91, content='Documenta procesos.')],

    )

    semantic_search.get_metadata_entries.return_value = {}

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_document_analysis.return_value = 'Segun Manual_Analista_Procesos.pdf...'

    logger = MagicMock()

    service = _build_service(chat_service, semantic_search, ai_response)

    service._logger = logger

    result = service.ask('¿Qué hace el analista de procesos?')

    assert result.source == 'documents'

    assert logger.info.call_args.args[3] is True

    assert logger.info.call_args.args[5] == 'HIGH'



def test_ask_logs_route_and_timing() -> None:

    chat_service = MagicMock(spec=ChatService)

    chat_service.process.return_value = ChatResult(

        question='¿Cuántos pedidos tenemos?',

        intent=ChatIntent.SALES_COUNT,

        data={'total_sales_orders': 5},

    )

    semantic_search = MagicMock(spec=SemanticSearchService)

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_business_analysis.return_value = 'Hay 5 pedidos.'

    logger = MagicMock()

    service = _build_service(chat_service, semantic_search, ai_response)

    service._logger = logger

    service.ask('¿Cuántos pedidos tenemos?')

    logger.info.assert_called_once()

    assert logger.info.call_args.args[1] == 'analytics'



def test_ask_routes_to_hybrid_with_full_snapshot() -> None:

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

    semantic_search.get_metadata_entries.return_value = {}

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_hybrid_business_analysis.return_value = 'Hay 100 clientes y se registran en el modulo de ventas.'

    classifier = QuestionClassifier()

    service = _build_service(chat_service, semantic_search, ai_response, classifier=classifier)

    result = service.ask(question)

    assert result.source == 'hybrid'

    ai_response.generate_hybrid_business_analysis.assert_called_once()

    call_kwargs = ai_response.generate_hybrid_business_analysis.call_args.kwargs

    assert call_kwargs['hybrid_context']['analytics_snapshot']['summary']['total_customers'] == 100



def test_ask_hybrid_logs_analytics_and_document_hits() -> None:

    question = '¿Cuál es el ticket promedio y cuál es el procedimiento de ventas?'

    chat_service = MagicMock(spec=ChatService)

    chat_service.process.return_value = ChatResult(

        question=question,

        intent=ChatIntent.SALES_AVERAGE_TICKET,

        data={'average_order_amount': '100.00'},

    )

    semantic_search = MagicMock(spec=SemanticSearchService)

    semantic_search.search.return_value = SemanticSearchResult(

        query=question,

        results=[SemanticSearchHit(document='Procedimiento_Ventas.docx', score=0.91, content='El procedimiento inicia con la cotizacion.')],

    )

    semantic_search.get_metadata_entries.return_value = {}

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_hybrid_business_analysis.return_value = 'El ticket promedio es 100 y el procedimiento inicia con la cotizacion.'

    logger = MagicMock()

    classifier = QuestionClassifier()

    service = _build_service(chat_service, semantic_search, ai_response, classifier=classifier)

    service._logger = logger

    service.ask(question)

    assert logger.info.call_args.args[1] == 'hybrid'

    assert logger.info.call_args.args[3] is True

    assert logger.info.call_args.args[9] == 1

    assert logger.info.call_args.args[10] == 1



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

    semantic_search.get_metadata_entries.return_value = {}

    ai_response = MagicMock(spec=AIResponseService)

    ai_response.generate_hybrid_business_analysis.return_value = 'Hay 5 pedidos. No hay procedimiento documental disponible.'

    classifier = QuestionClassifier()

    service = _build_service(chat_service, semantic_search, ai_response, classifier=classifier)

    result = service.ask(question)

    assert result.source == 'hybrid'

    call_kwargs = ai_response.generate_hybrid_business_analysis.call_args.kwargs

    assert call_kwargs['hybrid_context']['document_context']['total_matches'] == 0


