import unicodedata

from app.domain.hybrid_context import HybridContext
from app.domain.hybrid_insights import HybridInsights

class HybridInsightsService:

    def build_insights(self, question: str, hybrid_context: HybridContext) -> HybridInsights:
        payload = hybrid_context.to_dict()
        executive_insights = payload.get('executive_insights', {})
        document_context = payload.get('document_context', {})
        document_insights = payload.get('document_insights', {})
        analytics_snapshot = payload.get('analytics_snapshot', {})
        cross_source_findings: list[str] = []
        related_documents = list(document_insights.get('source_documents', []))
        dominant_customer = executive_insights.get('dominant_customer')
        if dominant_customer:
            customer_docs = self._find_related_documents(
                dominant_customer,
                document_context,
                ('cliente', 'clientes', 'comercial', 'cartera', 'venta'),
            )
            if customer_docs:
                cross_source_findings.append(
                    f'El cliente dominante {dominant_customer} tiene documentacion relacionada en {", ".join(customer_docs)}'
                )
                related_documents = self._merge_documents(related_documents, customer_docs)
        dominant_product = executive_insights.get('dominant_product')
        if dominant_product:
            product_docs = self._find_related_documents(
                dominant_product,
                document_context,
                ('producto', 'productos', 'manual', 'catalogo', 'ficha'),
            )
            if product_docs:
                cross_source_findings.append(
                    f'El producto dominante {dominant_product} aparece respaldado en {", ".join(product_docs)}'
                )
                related_documents = self._merge_documents(related_documents, product_docs)
        risk_flags = executive_insights.get('risk_flags') or []
        if risk_flags and document_context.get('total_matches', 0) > 0:
            top_document = document_context.get('top_document')
            cross_source_findings.append(
                f'Riesgo comercial observado ({risk_flags[0]}) con respaldo documental en {top_document}'
            )
            if top_document:
                related_documents = self._merge_documents(related_documents, [str(top_document)])
        if self._question_links_registration(question) and document_context.get('total_matches', 0) > 0:
            registration_docs = self._find_related_documents(
                question,
                document_context,
                ('registro', 'registran', 'cliente', 'procedimiento', 'manual'),
            )
            if registration_docs:
                cross_source_findings.append(
                    f'La pregunta combina metricas de clientes con procedimientos documentados en {", ".join(registration_docs)}'
                )
                related_documents = self._merge_documents(related_documents, registration_docs)
        confidence = self._compute_confidence(analytics_snapshot, document_insights, document_context, cross_source_findings)
        return HybridInsights(
            cross_source_findings=cross_source_findings,
            related_documents=related_documents,
            confidence=confidence,
        )

    @staticmethod
    def _normalize(value: str) -> str:
        lowered = value.lower().strip()
        return ''.join(
            character for character in unicodedata.normalize('NFD', lowered)
            if unicodedata.category(character) != 'Mn'
        )

    def _find_related_documents(
        self,
        anchor: str,
        document_context: dict[str, object],
        keywords: tuple[str, ...],
    ) -> list[str]:
        normalized_anchor = self._normalize(anchor)
        anchor_tokens = {token for token in normalized_anchor.replace(',', ' ').split() if len(token) > 3}
        matches: list[str] = []
        for item in document_context.get('documents', []):
            if not isinstance(item, dict):
                continue
            document_name = str(item.get('document_name', ''))
            content = str(item.get('content', ''))
            normalized_name = self._normalize(document_name)
            normalized_content = self._normalize(content)
            keyword_hit = any(keyword in normalized_name or keyword in normalized_content for keyword in keywords)
            anchor_hit = any(token in normalized_name or token in normalized_content for token in anchor_tokens)
            if keyword_hit or anchor_hit:
                matches.append(document_name)
        return list(dict.fromkeys(matches))

    @staticmethod
    def _merge_documents(current: list[str], extra: list[str]) -> list[str]:
        return list(dict.fromkeys([*current, *extra]))

    @staticmethod
    def _question_links_registration(question: str) -> bool:
        normalized = HybridInsightsService._normalize(question)
        return 'cliente' in normalized and any(token in normalized for token in ('registr', 'procedimiento', 'manual', 'como se'))

    @staticmethod
    def _compute_confidence(
        analytics_snapshot: dict[str, object],
        document_insights: dict[str, object],
        document_context: dict[str, object],
        cross_source_findings: list[str],
    ) -> str:
        has_analytics = bool(analytics_snapshot.get('summary'))
        has_documents = int(document_context.get('total_matches', 0)) > 0
        document_confidence = str(document_insights.get('confidence_level', 'LOW'))
        if has_analytics and has_documents and document_confidence == 'HIGH' and cross_source_findings:
            return 'HIGH'
        if has_analytics and has_documents and document_confidence in ('HIGH', 'MEDIUM'):
            return 'MEDIUM'
        if has_analytics and has_documents:
            return 'MEDIUM'
        if has_analytics or has_documents:
            return 'LOW'
        return 'LOW'
