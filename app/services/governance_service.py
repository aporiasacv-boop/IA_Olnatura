from datetime import date
from typing import Any

from app.domain.governance_context import GovernanceContext
from app.services.confidence_engine import ConfidenceEngine
from app.services.evidence_builder import EvidenceBuilder

class GovernanceService:

    def __init__(
        self,
        confidence_engine: ConfidenceEngine | None = None,
        evidence_builder: EvidenceBuilder | None = None,
    ):
        self._confidence = confidence_engine or ConfidenceEngine()
        self._evidence = evidence_builder or EvidenceBuilder()

    def build_analytics_governance(self, snapshot: dict[str, Any]) -> GovernanceContext:
        summary = snapshot.get('summary', {})
        financials = snapshot.get('financials', {})
        records = int(
            financials.get('total_lines')
            or financials.get('total_orders')
            or summary.get('total_orders')
            or 0
        )
        date_range = snapshot.get('date_range', {})
        snapshot_date = date_range.get('end_date') or date.today().isoformat()
        evidence = self._evidence.build_analytics_evidence(snapshot)
        limitations = self._analytics_limitations(records)
        return GovernanceContext(
            source_type='analytics',
            source_tables=['venta_lineas', 'ventas', 'clientes'],
            source_documents=[],
            confidence_level=self._confidence.analytics_level(records),
            snapshot_date=str(snapshot_date),
            records_analyzed=records,
            evidence=evidence,
            generated_at=GovernanceContext.now_iso(),
            limitations=limitations,
        )

    def build_document_governance(
        self,
        document_context: dict[str, Any],
        document_insights: dict[str, Any],
    ) -> GovernanceContext:
        total_matches = int(document_context.get('total_matches', 0))
        average_score = float(document_insights.get('average_score', 0))
        sources = list(document_insights.get('source_documents', []))
        evidence = self._evidence.build_document_evidence(document_context, document_insights)
        limitations = ['Sin respaldo analitico de ventas en esta consulta'] if total_matches > 0 else [
            'No se encontraron fragmentos documentales relevantes',
        ]
        return GovernanceContext(
            source_type='documents',
            source_tables=[],
            source_documents=sources,
            confidence_level=self._confidence.document_level(average_score, total_matches),
            snapshot_date=date.today().isoformat(),
            records_analyzed=total_matches,
            evidence=evidence,
            generated_at=GovernanceContext.now_iso(),
            limitations=limitations,
        )

    def build_hybrid_governance(
        self,
        hybrid_context: dict[str, Any],
        hybrid_insights: dict[str, Any],
    ) -> GovernanceContext:
        snapshot = hybrid_context.get('analytics_snapshot', {})
        summary = snapshot.get('summary', {})
        financials = snapshot.get('financials', {})
        records = int(
            financials.get('total_lines')
            or financials.get('total_orders')
            or summary.get('total_orders')
            or 0
        )
        document_context = hybrid_context.get('document_context', {})
        document_insights = hybrid_context.get('document_insights', {})
        analytics_level = self._confidence.analytics_level(records)
        document_level = self._confidence.document_level(
            float(document_insights.get('average_score', 0)),
            int(document_context.get('total_matches', 0)),
        )
        date_range = snapshot.get('date_range', {})
        snapshot_date = date_range.get('end_date') or date.today().isoformat()
        sources = list(document_insights.get('source_documents', []))
        evidence = self._evidence.build_hybrid_evidence(hybrid_context, hybrid_insights)
        return GovernanceContext(
            source_type='hybrid',
            source_tables=['venta_lineas', 'ventas', 'clientes'],
            source_documents=sources,
            confidence_level=self._confidence.hybrid_level(analytics_level, document_level),
            snapshot_date=str(snapshot_date),
            records_analyzed=records + int(document_context.get('total_matches', 0)),
            evidence=evidence,
            generated_at=GovernanceContext.now_iso(),
            limitations=self._hybrid_limitations(records, int(document_context.get('total_matches', 0))),
        )

    def build_memory_governance(
        self,
        memory_context: dict[str, Any],
        snapshot_count: int,
    ) -> GovernanceContext:
        latest = memory_context.get('latest_snapshot') or {}
        evidence = self._evidence.build_memory_evidence(memory_context)
        limitations = []
        if snapshot_count < 2:
            limitations.append('Historico limitado: se requieren al menos 2 snapshots para comparacion robusta')
        if not latest:
            limitations.append('No hay snapshots organizacionales persistidos')
        return GovernanceContext(
            source_type='memory',
            source_tables=['organizational_snapshots'],
            source_documents=[],
            confidence_level=self._confidence.memory_level(snapshot_count),
            snapshot_date=latest.get('snapshot_date'),
            records_analyzed=snapshot_count,
            evidence=evidence,
            generated_at=GovernanceContext.now_iso(),
            limitations=limitations,
        )

    def build_copilot_governance(self, copilot_context: dict[str, Any]) -> GovernanceContext:
        snapshot = copilot_context.get('analytics_snapshot', {})
        hybrid_insights = copilot_context.get('hybrid_insights', {})
        summary = snapshot.get('summary', {})
        financials = snapshot.get('financials', {})
        records = int(
            financials.get('total_lines')
            or financials.get('total_orders')
            or summary.get('total_orders')
            or 0
        )
        document_confidence = str(hybrid_insights.get('document_confidence_level', 'LOW'))
        document_matches = int(hybrid_insights.get('total_matches', 0)) if 'total_matches' in hybrid_insights else 0
        analytics_level = self._confidence.analytics_level(records)
        document_level = document_confidence if document_matches else 'LOW'
        if document_matches == 0:
            document_level = 'LOW'
        date_range = snapshot.get('date_range', {})
        snapshot_date = date_range.get('end_date') or date.today().isoformat()
        evidence = self._evidence.build_copilot_evidence(copilot_context)
        return GovernanceContext(
            source_type='copilot',
            source_tables=['venta_lineas', 'ventas', 'clientes'],
            source_documents=list(hybrid_insights.get('related_documents', [])),
            confidence_level=self._confidence.copilot_level(analytics_level, document_level),
            snapshot_date=str(snapshot_date),
            records_analyzed=records,
            evidence=evidence,
            generated_at=GovernanceContext.now_iso(),
            limitations=['Las recomendaciones del copilot no sustituyen revision humana'],
        )

    @staticmethod
    def _analytics_limitations(records: int) -> list[str]:
        if records < 50:
            return ['Volumen de registros limitado; la confianza estadistica es baja']
        if records < 100:
            return ['Volumen moderado de registros; validar hallazgos con contexto adicional']
        return []

    @staticmethod
    def _hybrid_limitations(records: int, document_matches: int) -> list[str]:
        limitations: list[str] = []
        if records < 100:
            limitations.append('Cobertura analitica parcial')
        if document_matches == 0:
            limitations.append('Sin respaldo documental para la pregunta')
        return limitations
