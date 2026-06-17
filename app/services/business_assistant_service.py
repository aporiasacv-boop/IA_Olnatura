import logging
import time
from dataclasses import dataclass
from app.services.ai_response_service import AIResponseService
from app.services.analytics_context_service import AnalyticsContextService
from app.services.chat_service import ChatService
from app.services.copilot_context_service import CopilotContextService
from app.services.document_context_service import DocumentContextService
from app.services.document_insights_service import DocumentInsightsService
from app.services.evidence_builder import EvidenceBuilder
from app.services.governance_service import GovernanceService
from app.services.hybrid_context_service import HybridContextService
from app.services.hybrid_insights_service import HybridInsightsService
from app.services.question_classifier import QuestionClassifier
from app.services.semantic_search_service import SemanticSearchService
from app.services.snapshot_memory_service import SnapshotMemoryService

_EMPTY_DOCUMENT_CONTEXT_ANSWER = 'No se encontraron fragmentos relevantes en los documentos indexados para responder la pregunta.'

@dataclass(frozen=True)
class AssistantResult:
    source: str
    answer: str

@dataclass(frozen=True)
class HybridAnalysisResult:
    confidence: str
    sources: list[str]
    answer: str

@dataclass(frozen=True)
class CopilotResult:
    attention_points: list[str]
    answer: str

@dataclass(frozen=True)
class GovernanceResult:
    confidence: str
    evidence: list[str]
    answer: str
    source_type: str
    source_tables: list[str]
    source_documents: list[str]
    snapshot_date: str | None
    records_analyzed: int
    generated_at: str

class BusinessAssistantService:

    def __init__(
        self,
        chat_service: ChatService,
        semantic_search_service: SemanticSearchService,
        ai_response_service: AIResponseService,
        analytics_context_service: AnalyticsContextService,
        document_context_service: DocumentContextService | None = None,
        document_insights_service: DocumentInsightsService | None = None,
        hybrid_context_service: HybridContextService | None = None,
        hybrid_insights_service: HybridInsightsService | None = None,
        copilot_context_service: CopilotContextService | None = None,
        snapshot_memory_service: SnapshotMemoryService | None = None,
        governance_service: GovernanceService | None = None,
        evidence_builder: EvidenceBuilder | None = None,
        classifier: QuestionClassifier | None = None,
        logger: logging.Logger | None = None,
    ):
        self._chat_service = chat_service
        self._semantic_search_service = semantic_search_service
        self._ai_response_service = ai_response_service
        self._analytics_context_service = analytics_context_service
        self._document_context_service = document_context_service or DocumentContextService(semantic_search_service)
        self._document_insights_service = document_insights_service or DocumentInsightsService()
        self._hybrid_context_service = hybrid_context_service or HybridContextService(
            analytics_context_service,
            self._document_context_service,
            self._document_insights_service,
        )
        self._hybrid_insights_service = hybrid_insights_service or HybridInsightsService()
        self._copilot_context_service = copilot_context_service
        self._snapshot_memory_service = snapshot_memory_service
        self._governance_service = governance_service or GovernanceService()
        self._evidence_builder = evidence_builder or EvidenceBuilder()
        self._classifier = classifier or QuestionClassifier()
        self._logger = logger or logging.getLogger(__name__)

    def ask(self, question: str) -> AssistantResult:
        started_at = time.perf_counter()
        self._chat_service.process(question)
        executive_mode = False
        document_mode = False
        hybrid_mode = False
        copilot_mode = False
        memory_mode = False
        governance_mode = False
        if self._classifier.is_hybrid(question):
            route_selected = 'hybrid'
            response_source = 'hybrid'
            hybrid_mode = True
            answer, analytics_hits, document_hits, hybrid_insights = self._answer_hybrid(question)
            copilot_insights = None
            memory_insights = None
            governance_context = None
        elif self._classifier.is_copilot_question(question):
            route_selected = 'copilot'
            response_source = 'copilot'
            copilot_mode = True
            analytics_hits = 1
            document_hits = 0
            answer, copilot_insights = self._answer_copilot(question)
            hybrid_insights = None
            memory_insights = None
            governance_context = None
        elif self._classifier.is_memory_question(question):
            route_selected = 'memory'
            response_source = 'memory'
            memory_mode = True
            analytics_hits = 1
            document_hits = 0
            answer, memory_insights = self._answer_memory(question)
            hybrid_insights = None
            copilot_insights = None
        elif self._classifier.is_governance_question(question):
            route_selected = 'governance'
            response_source = 'governance'
            governance_mode = True
            analytics_hits = 1
            document_hits = 0
            answer, governance_context = self._answer_governance(question)
            hybrid_insights = None
            copilot_insights = None
            memory_insights = None
        elif self._classifier.is_executive_question(question):
            route_selected = 'executive'
            response_source = 'executive'
            executive_mode = True
            analytics_hits = 1
            document_hits = 0
            answer, executive_insights = self._answer_executive(question)
            document_insights = None
            hybrid_insights = None
            copilot_insights = None
            memory_insights = None
            governance_context = None
        elif self._classifier.is_analytics_question(question):
            route_selected = 'analytics'
            response_source = 'analytics'
            analytics_hits = 1
            document_hits = 0
            answer = self._answer_analytics(question)
            executive_insights = None
            document_insights = None
            hybrid_insights = None
            copilot_insights = None
            memory_insights = None
            governance_context = None
        else:
            route_selected = 'documents'
            response_source = 'documents'
            analytics_hits = 0
            document_mode = True
            answer, document_hits, document_insights = self._answer_from_documents(question)
            executive_insights = None
            hybrid_insights = None
            copilot_insights = None
            memory_insights = None
            governance_context = None
        execution_time_ms = (time.perf_counter() - started_at) * 1000
        if hybrid_mode and hybrid_insights is not None:
            self._logger.info(
                'route_selected=%s response_source=%s hybrid_mode=%s analytics_used=%s documents_used=%s executive_used=%s cross_source_findings_count=%s confidence=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
                route_selected,
                response_source,
                True,
                True,
                int(hybrid_insights.get('documents_used', document_hits > 0)),
                bool(hybrid_insights.get('executive_used')),
                len(hybrid_insights.get('cross_source_findings', [])),
                hybrid_insights.get('confidence'),
                analytics_hits,
                document_hits,
                execution_time_ms,
            )
        elif copilot_mode and copilot_insights is not None:
            self._logger.info(
                'route_selected=%s response_source=%s copilot_mode=%s attention_points_count=%s recommended_reviews_count=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
                route_selected,
                response_source,
                True,
                len(copilot_insights.get('attention_points', [])),
                len(copilot_insights.get('recommended_reviews', [])),
                analytics_hits,
                document_hits,
                execution_time_ms,
            )
        elif memory_mode and memory_insights is not None:
            self._logger.info(
                'route_selected=%s response_source=%s memory_mode=%s changes_count=%s stable_findings_count=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
                route_selected,
                response_source,
                True,
                len(memory_insights.get('changes', [])),
                len(memory_insights.get('stable_findings', [])),
                analytics_hits,
                document_hits,
                execution_time_ms,
            )
        elif governance_mode and governance_context is not None:
            self._logger.info(
                'route_selected=%s response_source=%s governance_mode=%s confidence_level=%s evidence_count=%s records_analyzed=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
                route_selected,
                response_source,
                True,
                governance_context.get('confidence_level'),
                len(governance_context.get('evidence', [])),
                governance_context.get('records_analyzed'),
                analytics_hits,
                document_hits,
                execution_time_ms,
            )
        elif executive_mode and executive_insights is not None:
            self._logger.info(
                'route_selected=%s response_source=%s executive_mode=%s risk_flags_count=%s top_customer_share=%s top_product_share=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
                route_selected,
                response_source,
                True,
                len(executive_insights.get('risk_flags', [])),
                executive_insights.get('top_customer_share'),
                executive_insights.get('top_product_share'),
                analytics_hits,
                document_hits,
                execution_time_ms,
            )
        elif document_mode and document_insights is not None:
            self._logger.info(
                'route_selected=%s response_source=%s document_mode=%s top_document=%s confidence_level=%s total_matches=%s average_score=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
                route_selected,
                response_source,
                True,
                document_insights.get('top_document'),
                document_insights.get('confidence_level'),
                document_insights.get('total_matches'),
                document_insights.get('average_score'),
                analytics_hits,
                document_hits,
                execution_time_ms,
            )
        else:
            self._logger.info(
                'route_selected=%s response_source=%s analytics_hits=%s document_hits=%s execution_time_ms=%.2f',
                route_selected,
                response_source,
                analytics_hits,
                document_hits,
                execution_time_ms,
            )
        return AssistantResult(source=response_source, answer=answer.strip())

    def analyze_hybrid(self, question: str) -> HybridAnalysisResult:
        hybrid_context = self._hybrid_context_service.build_context(question)
        hybrid_insights = self._hybrid_insights_service.build_insights(question, hybrid_context)
        document_hits = int(hybrid_context.document_context.get('total_matches', 0))
        executive_insights = hybrid_context.executive_insights
        insights_payload = self._build_hybrid_logging_payload(hybrid_insights, document_hits, executive_insights)
        answer = self._ai_response_service.generate_hybrid_business_analysis(
            question=question,
            hybrid_context=hybrid_context.to_dict(),
            hybrid_insights=hybrid_insights.to_dict(),
        )
        self._logger.info(
            'hybrid_mode=%s analytics_used=%s documents_used=%s executive_used=%s cross_source_findings_count=%s confidence=%s',
            True,
            True,
            insights_payload['documents_used'],
            insights_payload['executive_used'],
            len(hybrid_insights.cross_source_findings),
            hybrid_insights.confidence,
        )
        return HybridAnalysisResult(
            confidence=hybrid_insights.confidence,
            sources=hybrid_insights.related_documents,
            answer=answer.strip(),
        )

    def ask_copilot(self, question: str) -> CopilotResult:
        copilot_context = self._get_copilot_context_service().build_context(question)
        copilot_insights = copilot_context.copilot_insights
        answer = self._ai_response_service.generate_copilot_response(
            question=question,
            copilot_context=copilot_context.to_dict(),
        )
        self._logger.info(
            'copilot_mode=%s attention_points_count=%s recommended_reviews_count=%s',
            True,
            len(copilot_insights.get('attention_points', [])),
            len(copilot_insights.get('recommended_reviews', [])),
        )
        return CopilotResult(
            attention_points=list(copilot_insights.get('attention_points', [])),
            answer=answer.strip(),
        )

    def ask_governance(self, question: str) -> GovernanceResult:
        answer, governance_context = self._answer_governance(question)
        flattened = self._evidence_builder.flatten_evidence(governance_context.get('evidence', []))
        self._logger.info(
            'governance_mode=%s confidence_level=%s evidence_count=%s records_analyzed=%s',
            True,
            governance_context.get('confidence_level'),
            len(governance_context.get('evidence', [])),
            governance_context.get('records_analyzed'),
        )
        return GovernanceResult(
            confidence=str(governance_context.get('confidence_level', 'LOW')),
            evidence=flattened,
            answer=answer.strip(),
            source_type=str(governance_context.get('source_type', 'analytics')),
            source_tables=list(governance_context.get('source_tables', [])),
            source_documents=list(governance_context.get('source_documents', [])),
            snapshot_date=governance_context.get('snapshot_date'),
            records_analyzed=int(governance_context.get('records_analyzed', 0)),
            generated_at=str(governance_context.get('generated_at', '')),
        )

    def _get_copilot_context_service(self) -> CopilotContextService:
        if self._copilot_context_service is None:
            from app.services.copilot_insights_service import CopilotInsightsService
            self._copilot_context_service = CopilotContextService(
                self._hybrid_context_service,
                self._hybrid_insights_service,
                CopilotInsightsService(),
            )
        return self._copilot_context_service

    def _get_snapshot_memory_service(self) -> SnapshotMemoryService:
        if self._snapshot_memory_service is None:
            raise RuntimeError('SnapshotMemoryService no configurado')
        return self._snapshot_memory_service

    def _answer_governance(self, question: str) -> tuple[str, dict[str, object]]:
        snapshot = self._analytics_context_service.build_snapshot().to_dict()
        governance = self._governance_service.build_analytics_governance(snapshot)
        governance_payload = governance.to_dict()
        base_answer = self._build_governance_base_answer(governance_payload)
        answer = self._ai_response_service.generate_governed_response(
            question=question,
            answer=base_answer,
            governance_context=governance_payload,
        )
        return answer.strip(), governance_payload

    @staticmethod
    def _build_governance_base_answer(governance_context: dict[str, object]) -> str:
        evidence = governance_context.get('evidence', [])
        if isinstance(evidence, list) and evidence:
            first = evidence[0]
            if isinstance(first, dict) and first.get('statement'):
                return str(first['statement'])
        return 'Informacion derivada del snapshot analitico empresarial actual.'

    def _answer_memory(self, question: str) -> tuple[str, dict[str, object]]:
        memory_context = self._get_snapshot_memory_service().build_memory_context()
        answer = self._ai_response_service.generate_memory_analysis(
            question=question,
            memory_context=memory_context,
        )
        memory_insights = memory_context.get('memory_insights', {})
        return answer.strip(), memory_insights

    def _answer_copilot(self, question: str) -> tuple[str, dict[str, object]]:
        copilot_context = self._get_copilot_context_service().build_context(question)
        answer = self._ai_response_service.generate_copilot_response(
            question=question,
            copilot_context=copilot_context.to_dict(),
        )
        return answer.strip(), copilot_context.copilot_insights

    def _answer_analytics(self, question: str) -> str:
        snapshot = self._analytics_context_service.build_snapshot().to_dict()
        return self._ai_response_service.generate_business_analysis(question=question, snapshot=snapshot)

    def _answer_executive(self, question: str) -> tuple[str, dict[str, object]]:
        snapshot = self._analytics_context_service.build_snapshot().to_dict()
        executive_insights = snapshot.get('executive_insights', {})
        answer = self._ai_response_service.generate_executive_summary(question=question, snapshot=snapshot)
        return answer, executive_insights

    def _answer_hybrid(self, question: str) -> tuple[str, int, int, dict[str, object]]:
        hybrid_context = self._hybrid_context_service.build_context(question)
        hybrid_insights = self._hybrid_insights_service.build_insights(question, hybrid_context)
        document_hits = int(hybrid_context.document_context.get('total_matches', 0))
        insights_payload = self._build_hybrid_logging_payload(
            hybrid_insights,
            document_hits,
            hybrid_context.executive_insights,
        )
        answer = self._ai_response_service.generate_hybrid_business_analysis(
            question=question,
            hybrid_context=hybrid_context.to_dict(),
            hybrid_insights=hybrid_insights.to_dict(),
        )
        return answer, 1, document_hits, insights_payload

    def _answer_from_documents(self, question: str) -> tuple[str, int, dict[str, object] | None]:
        document_context = self._document_context_service.build_context(question)
        if document_context.total_matches == 0:
            return _EMPTY_DOCUMENT_CONTEXT_ANSWER, 0, {
                'total_matches': 0,
                'confidence_level': 'LOW',
                'top_document': None,
                'source_documents': [],
                'average_score': 0.0,
            }
        document_insights = self._document_insights_service.build_insights(document_context)
        answer = self._ai_response_service.generate_document_analysis(
            question=question,
            document_context=document_context.to_dict(),
            document_insights=document_insights.to_dict(),
        )
        return answer, document_context.total_matches, document_insights.to_dict()

    @staticmethod
    def _build_hybrid_logging_payload(
        hybrid_insights: object,
        document_hits: int,
        executive_insights: dict[str, object],
    ) -> dict[str, object]:
        findings = getattr(hybrid_insights, 'cross_source_findings', [])
        confidence = getattr(hybrid_insights, 'confidence', 'LOW')
        return {
            'cross_source_findings': list(findings),
            'confidence': confidence,
            'documents_used': document_hits > 0,
            'executive_used': bool(executive_insights),
        }
