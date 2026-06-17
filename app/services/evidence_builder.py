from typing import Any

class EvidenceBuilder:

    def build_analytics_evidence(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        summary = snapshot.get('summary', {})
        financials = snapshot.get('financials', {})
        executive = snapshot.get('executive_insights', {})
        records = int(financials.get('total_lines') or financials.get('total_orders') or summary.get('total_orders') or 0)
        total_revenue = financials.get('total_revenue', '0')
        dominant_customer = executive.get('dominant_customer')
        top_share = executive.get('top_customer_share')
        items: list[dict[str, Any]] = []
        if dominant_customer and top_share is not None:
            items.append({
                'statement': f'{dominant_customer} concentra {float(top_share):.1f}% de los ingresos observados',
                'evidence': [
                    f'{records} lineas de venta analizadas' if records else 'Pedidos sincronizados desde Dynamics',
                    f'Revenue total: {total_revenue} MXN',
                    'Cliente dominante identificado en venta_lineas',
                ],
            })
        dominant_product = executive.get('dominant_product')
        product_share = executive.get('top_product_share')
        if dominant_product and product_share is not None:
            items.append({
                'statement': f'El producto dominante {dominant_product} representa {float(product_share):.1f}% del ingreso',
                'evidence': [
                    f'{records} lineas de venta analizadas' if records else 'Lineas de venta sincronizadas',
                    f'Revenue total: {total_revenue} MXN',
                    'Producto dominante identificado en venta_lineas',
                ],
            })
        if not items:
            items.append({
                'statement': 'Metricas comerciales derivadas del snapshot analitico actual',
                'evidence': [
                    f'{int(summary.get("total_customers", 0))} clientes en cartera',
                    f'{int(summary.get("total_orders", 0))} pedidos registrados',
                    f'Revenue total: {total_revenue} MXN',
                ],
            })
        return items

    def build_document_evidence(
        self,
        document_context: dict[str, Any],
        document_insights: dict[str, Any],
    ) -> list[dict[str, Any]]:
        total_matches = int(document_context.get('total_matches', 0))
        top_document = document_context.get('top_document')
        average_score = float(document_insights.get('average_score', 0))
        sources = list(document_insights.get('source_documents', []))
        if total_matches == 0:
            return [{
                'statement': 'No se encontraron fragmentos documentales relevantes',
                'evidence': ['Indice semantico consultado sin coincidencias'],
            }]
        return [{
            'statement': f'Informacion respaldada por {total_matches} fragmento(s) documental(es)',
            'evidence': [
                f'Documento principal: {top_document}' if top_document else 'Documento principal no identificado',
                f'Puntuacion promedio de relevancia: {average_score:.2f}',
                f'Fuentes consultadas: {", ".join(sources) if sources else "sin fuentes nombradas"}',
            ],
        }]

    def build_hybrid_evidence(
        self,
        hybrid_context: dict[str, Any],
        hybrid_insights: dict[str, Any],
    ) -> list[dict[str, Any]]:
        analytics_items = self.build_analytics_evidence(hybrid_context.get('analytics_snapshot', {}))
        document_items = self.build_document_evidence(
            hybrid_context.get('document_context', {}),
            hybrid_context.get('document_insights', {}),
        )
        cross_findings = list(hybrid_insights.get('cross_source_findings', []))
        if cross_findings:
            analytics_items.append({
                'statement': 'Hallazgo cruzado entre analytics y documentos',
                'evidence': cross_findings,
            })
        return analytics_items + document_items

    def build_memory_evidence(self, memory_context: dict[str, Any]) -> list[dict[str, Any]]:
        latest = memory_context.get('latest_snapshot') or {}
        previous = memory_context.get('previous_snapshot')
        insights = memory_context.get('memory_insights', {})
        items: list[dict[str, Any]] = []
        if latest:
            items.append({
                'statement': f'Snapshot organizacional del {latest.get("snapshot_date", "periodo actual")}',
                'evidence': [
                    f'{int(latest.get("total_customers", 0))} clientes registrados',
                    f'Revenue: {latest.get("total_revenue", "0")} MXN',
                    f'Cliente dominante: {latest.get("top_customer") or "no identificado"}',
                ],
            })
        if previous:
            items.append({
                'statement': f'Comparacion con snapshot anterior del {previous.get("snapshot_date")}',
                'evidence': list(insights.get('changes', [])) + list(insights.get('stable_findings', [])),
            })
        elif latest:
            items.append({
                'statement': 'Sin snapshot anterior para comparacion temporal',
                'evidence': list(insights.get('stable_findings', [])) + list(insights.get('new_findings', [])),
            })
        return items or [{
            'statement': 'Sin snapshots organizacionales disponibles',
            'evidence': ['No hay historico persistido en organizational_snapshots'],
        }]

    def build_copilot_evidence(self, copilot_context: dict[str, Any]) -> list[dict[str, Any]]:
        hybrid_items = self.build_hybrid_evidence(
            {
                'analytics_snapshot': copilot_context.get('analytics_snapshot', {}),
                'document_context': copilot_context.get('hybrid_insights', {}),
                'document_insights': copilot_context.get('hybrid_insights', {}),
            },
            copilot_context.get('hybrid_insights', {}),
        )
        copilot_insights = copilot_context.get('copilot_insights', {})
        attention = list(copilot_insights.get('attention_points', []))
        if attention:
            hybrid_items.append({
                'statement': 'Puntos de atencion identificados por Business Copilot',
                'evidence': attention,
            })
        return hybrid_items

    @staticmethod
    def flatten_evidence(evidence: list[dict[str, Any]]) -> list[str]:
        flattened: list[str] = []
        for item in evidence:
            flattened.append(str(item.get('statement', '')))
            flattened.extend(str(line) for line in item.get('evidence', []))
        return [line for line in flattened if line]
