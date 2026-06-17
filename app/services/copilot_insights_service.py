from typing import Any

from app.domain.copilot_insights import CopilotInsights

class CopilotInsightsService:

    def build_insights(
        self,
        analytics_snapshot: dict[str, Any],
        executive_insights: dict[str, Any],
        hybrid_insights: dict[str, Any],
    ) -> CopilotInsights:
        observations: list[str] = []
        attention_points: list[str] = []
        recommended_reviews: list[str] = []
        top_customer_share = float(executive_insights.get('top_customer_share', 0))
        top_5_customer_share = float(executive_insights.get('top_5_customer_share', 0))
        top_product_share = float(executive_insights.get('top_product_share', 0))
        invoice_rate = float(executive_insights.get('invoice_rate', 100))
        dominant_customer = executive_insights.get('dominant_customer')
        dominant_product = executive_insights.get('dominant_product')
        revenue_concentration = str(executive_insights.get('revenue_concentration', ''))
        if 30 <= top_customer_share < 50 or revenue_concentration == 'Concentracion comercial moderada':
            label = f' en {dominant_customer}' if dominant_customer else ''
            observations.append(f'Concentracion comercial moderada{label} ({top_customer_share:.1f}%)')
            attention_points.append('Dependencia de principales clientes')
            recommended_reviews.append('Revisar periodicamente la dependencia de los principales clientes.')
        if top_customer_share >= 50 or revenue_concentration == 'Alta concentracion comercial':
            label = f' asociado a {dominant_customer}' if dominant_customer else ''
            observations.append(f'Alta concentracion comercial{label} ({top_customer_share:.1f}%)')
            attention_points.append('Riesgo comercial del cliente dominante')
            recommended_reviews.append('Monitorear riesgo comercial asociado al cliente dominante.')
        if top_5_customer_share > 80:
            observations.append(f'Los cinco principales clientes concentran el {top_5_customer_share:.1f}% de los ingresos')
            attention_points.append('Diversificacion de cartera')
            recommended_reviews.append('Analizar diversificacion de cartera.')
        if top_product_share > 40:
            label = dominant_product or 'producto principal'
            observations.append(f'Dependencia relevante del producto {label} ({top_product_share:.1f}% de ingresos)')
            attention_points.append('Dependencia del producto principal')
            recommended_reviews.append('Revisar dependencia de ingresos respecto al producto principal.')
        document_confidence = hybrid_insights.get('document_confidence_level') or hybrid_insights.get('confidence')
        if document_confidence == 'LOW':
            observations.append('La confianza documental asociada a la consulta es baja')
            attention_points.append('Confianza documental limitada')
            recommended_reviews.append('Validar documentacion adicional relacionada.')
        if invoice_rate < 80:
            observations.append(f'La tasa de facturacion observada es del {invoice_rate:.1f}%')
            attention_points.append('Pedidos pendientes de facturacion')
            recommended_reviews.append('Revisar pedidos pendientes de facturacion.')
        risk_flags = executive_insights.get('risk_flags') or []
        for flag in risk_flags:
            if flag not in observations:
                observations.append(str(flag))
        cross_findings = hybrid_insights.get('cross_source_findings') or []
        for finding in cross_findings[:3]:
            observations.append(str(finding))
        financials = analytics_snapshot.get('financials') or {}
        total_revenue = financials.get('total_revenue')
        if total_revenue and float(total_revenue) > 0 and not observations:
            observations.append(f'Ingresos registrados por {total_revenue} en lineas de venta sincronizadas')
        return CopilotInsights(
            observations=self._dedupe(observations),
            attention_points=self._dedupe(attention_points),
            recommended_reviews=self._dedupe(recommended_reviews),
        )

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        return list(dict.fromkeys(items))
