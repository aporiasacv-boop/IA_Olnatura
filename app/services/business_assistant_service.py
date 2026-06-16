import logging
import time
from dataclasses import dataclass
from app.domain.chat import ChatIntent
from app.services.ai_response_service import AIResponseService
from app.services.chat_service import ChatService
from app.services.context_fusion_service import ContextFusionService
from app.services.question_classifier import QuestionClassifier
from app.services.semantic_search_service import SemanticSearchService

_ANALYTICS_INTENTS = frozenset({
    ChatIntent.CUSTOMERS_COUNT,
    ChatIntent.SALES_COUNT,
    ChatIntent.SALES_TOTAL_AMOUNT,
    ChatIntent.SALES_AVERAGE_TICKET,
    ChatIntent.TOP_CUSTOMERS,
})

_EMPTY_DOCUMENT_CONTEXT_ANSWER = 'No se encontraron fragmentos relevantes en los documentos indexados para responder la pregunta.'

@dataclass(frozen=True)
class AssistantResult:
    source: str
    answer: str

class BusinessAssistantService:

    def __init__(
        self,
        chat_service: ChatService,
        semantic_search_service: SemanticSearchService,
        ai_response_service: AIResponseService,
        context_fusion_service: ContextFusionService | None = None,
        classifier: QuestionClassifier | None = None,
        logger: logging.Logger | None = None,
    ):
        self._chat_service = chat_service
        self._semantic_search_service = semantic_search_service
        self._ai_response_service = ai_response_service
        self._context_fusion_service = context_fusion_service or ContextFusionService()
        self._classifier = classifier or QuestionClassifier()
        self._logger = logger or logging.getLogger(__name__)

    def ask(self, question: str) -> AssistantResult:
        started_at = time.perf_counter()
        chat_result = self._chat_service.process(question)
        if self._classifier.is_hybrid(question) and chat_result.intent in _ANALYTICS_INTENTS:
            route_selected = 'hybrid'
            response_source = 'hybrid'
            answer, analytics_hits, document_hits = self._answer_hybrid(question, chat_result)
        elif chat_result.intent in _ANALYTICS_INTENTS:
            route_selected = 'analytics'
            response_source = 'analytics'
            analytics_hits = 1 if chat_result.data is not None else 0
            document_hits = 0
            answer = self._ai_response_service.generate(
                question=question,
                intent=chat_result.intent.value,
                data=chat_result.data,
            )
        else:
            route_selected = 'documents'
            response_source = 'documents'
            analytics_hits = 0
            answer, document_hits = self._answer_from_documents(question)
        execution_time_ms = (time.perf_counter() - started_at) * 1000
        self._logger.info(
            'route_selected=%s response_source=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
            route_selected,
            response_source,
            analytics_hits,
            document_hits,
            execution_time_ms,
        )
        return AssistantResult(source=response_source, answer=answer.strip())

    def _answer_hybrid(self, question: str, chat_result) -> tuple[str, int, int]:
        search_result = self._semantic_search_service.search(question)
        document_results = [
            {
                'document': item.document,
                'score': item.score,
                'content': item.content,
            }
            for item in search_result.results
        ]
        fused_context = self._context_fusion_service.fuse(
            intent=chat_result.intent.value,
            analytics_data=chat_result.data,
            document_results=document_results,
        )
        answer = self._ai_response_service.generate_hybrid(question=question, context=fused_context)
        return answer, fused_context.analytics_hits, fused_context.document_hits

    def _answer_from_documents(self, question: str) -> tuple[str, int]:
        search_result = self._semantic_search_service.search(question)
        if not search_result.results:
            return _EMPTY_DOCUMENT_CONTEXT_ANSWER, 0
        context = [
            {
                'document': item.document,
                'score': item.score,
                'content': item.content,
            }
            for item in search_result.results
        ]
        answer = self._ai_response_service.generate_from_documents(question=question, results=context)
        return answer, len(context)
