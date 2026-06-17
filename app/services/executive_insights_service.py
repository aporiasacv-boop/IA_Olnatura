from decimal import Decimal
from typing import Any

from app.domain.executive_insights import ExecutiveInsights

class ExecutiveInsightsService:

    def build_from_financials(self, financials: dict[str, Any]) -> ExecutiveInsights:
        total_revenue = Decimal(str(financials.get('total_revenue', '0')))
        top_customers = financials.get('top_customers_by_revenue') or []
        top_products = financials.get('top_products') or []
        sales_by_status = financials.get('sales_by_status') or []
        top_customer_share = 0.0
        top_5_customer_share = 0.0
        dominant_customer: str | None = None
        if total_revenue > 0 and top_customers:
            leading = top_customers[0]
            dominant_customer = leading.get('customer_name') or leading.get('customer_account')
            top_customer_share = float(Decimal(str(leading['total_revenue'])) / total_revenue * 100)
            top_five_total = sum(
                Decimal(str(item['total_revenue']))
                for item in top_customers[:5]
            )
            top_5_customer_share = float(top_five_total / total_revenue * 100)
        top_product_share = 0.0
        dominant_product: str | None = None
        if total_revenue > 0 and top_products:
            leading_product = top_products[0]
            dominant_product = leading_product.get('product_name') or leading_product.get('product_number')
            top_product_share = float(Decimal(str(leading_product['total_revenue'])) / total_revenue * 100)
        total_lines = sum(int(item.get('count', 0)) for item in sales_by_status)
        invoiced_lines = sum(
            int(item.get('count', 0))
            for item in sales_by_status
            if str(item.get('status', '')).lower() == 'invoiced'
        )
        invoice_rate = round((invoiced_lines / total_lines * 100) if total_lines > 0 else 0.0, 2)
        revenue_concentration = self._revenue_concentration_label(top_customer_share)
        risk_flags = self._build_risk_flags(top_customer_share, top_product_share, invoice_rate)
        return ExecutiveInsights(
            top_customer_share=round(top_customer_share, 2),
            top_5_customer_share=round(top_5_customer_share, 2),
            top_product_share=round(top_product_share, 2),
            dominant_customer=dominant_customer,
            dominant_product=dominant_product,
            invoice_rate=invoice_rate,
            revenue_concentration=revenue_concentration,
            risk_flags=risk_flags,
        )

    @staticmethod
    def _revenue_concentration_label(top_customer_share: float) -> str:
        if top_customer_share >= 50:
            return 'Alta concentracion comercial'
        if top_customer_share >= 30:
            return 'Concentracion comercial moderada'
        return 'Concentracion comercial dispersa'

    @staticmethod
    def _build_risk_flags(
        top_customer_share: float,
        top_product_share: float,
        invoice_rate: float,
    ) -> list[str]:
        flags: list[str] = []
        if top_customer_share >= 50:
            flags.append('Alta dependencia comercial de un solo cliente')
        elif top_customer_share >= 30:
            flags.append('Concentracion comercial moderada')
        if top_product_share >= 50:
            flags.append('Alta dependencia de un solo producto')
        if invoice_rate < 80:
            flags.append('Existen pedidos pendientes de facturacion')
        return flags

    def is_fully_invoiced(self, insights: ExecutiveInsights) -> bool:
        return insights.invoice_rate == 100.0
