from decimal import Decimal
from app.domain.analytics import ClienteVentas
from app.domain.analytics_context import (
    AnalyticsContextSnapshot,
    AnalyticsDateRange,
    AnalyticsInsights,
    CustomerConcentration,
)
from app.services.analytics_service import AnalyticsService
from app.services.financial_analytics_service import FinancialAnalyticsService

class AnalyticsContextService:

    def __init__(
        self,
        analytics_service: AnalyticsService,
        financial_analytics_service: FinancialAnalyticsService,
        top_customers_limit: int = 10,
        top_products_limit: int = 10,
    ):
        self._analytics = analytics_service
        self._financial_analytics = financial_analytics_service
        self._top_customers_limit = top_customers_limit
        self._top_products_limit = top_products_limit

    def build_snapshot(self) -> AnalyticsContextSnapshot:
        summary = self._analytics.sales_summary()
        total_customers = self._analytics.count_clientes()
        sales_by_status = self._analytics.sales_by_status()
        top_customers = self._analytics.top_customers(limit=self._top_customers_limit)
        start_date, end_date = self._analytics.sales_date_range()
        ventas_por_cliente = self._analytics.ventas_por_cliente()
        financials = self._build_financials()
        insights = self._build_insights(ventas_por_cliente, summary.total_amount, financials)
        return AnalyticsContextSnapshot(
            summary={
                'total_customers': total_customers,
                'total_orders': summary.total_orders,
                'total_sales_amount': self._decimal_value(summary.total_amount),
                'average_ticket': self._decimal_value(summary.average_order_amount),
            },
            sales_by_status=[
                {'status': item.status, 'count': item.count}
                for item in sales_by_status
            ],
            top_customers=[
                {
                    'customer_account': item.customer_account,
                    'customer_name': item.customer_name,
                    'orders': item.orders,
                    'total_amount': self._decimal_value(item.total_amount),
                }
                for item in top_customers
            ],
            date_range=AnalyticsDateRange(
                start_date=start_date.isoformat() if start_date else None,
                end_date=end_date.isoformat() if end_date else None,
            ),
            insights=insights,
            financials=financials,
        )

    def _build_financials(self) -> dict[str, object]:
        financial_summary = self._financial_analytics.financial_summary()
        top_customers = self._financial_analytics.top_customers_by_revenue(self._top_customers_limit)
        top_products = self._financial_analytics.top_products_by_revenue(self._top_products_limit)
        sales_by_status = self._financial_analytics.sales_by_line_status()
        return {
            'total_revenue': self._decimal_value(financial_summary.total_revenue),
            'average_order_value': self._decimal_value(financial_summary.average_order_value),
            'total_lines': financial_summary.total_lines,
            'total_orders': financial_summary.total_orders,
            'top_customers_by_revenue': [
                {
                    'customer_account': item.customer_account,
                    'customer_name': item.customer_name,
                    'lines': item.lines,
                    'total_revenue': self._decimal_value(item.total_revenue),
                }
                for item in top_customers
            ],
            'top_products': [
                {
                    'product_number': item.product_number,
                    'product_name': item.product_name,
                    'lines': item.lines,
                    'total_revenue': self._decimal_value(item.total_revenue),
                }
                for item in top_products
            ],
            'sales_by_status': [
                {
                    'status': item.status,
                    'count': item.count,
                    'total_revenue': self._decimal_value(item.total_revenue),
                }
                for item in sales_by_status
            ],
        }

    def _build_insights(
        self,
        ventas_por_cliente: list[ClienteVentas],
        header_total_amount: Decimal,
        financials: dict[str, object],
    ) -> AnalyticsInsights:
        financial_total = Decimal(str(financials.get('total_revenue', '0')))
        if financial_total > 0 and financials.get('top_customers_by_revenue'):
            top_customer = financials['top_customers_by_revenue'][0]
            leading_name = top_customer.get('customer_name') or top_customer.get('customer_account')
            largest_share = float(Decimal(str(top_customer['total_revenue'])) / financial_total * 100)
            top_five_total = sum(
                Decimal(str(item['total_revenue']))
                for item in financials['top_customers_by_revenue'][:5]
            )
            top_five_share = float(top_five_total / financial_total * 100)
            customers_with_sales = len(financials['top_customers_by_revenue'])
            return AnalyticsInsights(
                largest_customer_share=round(largest_share, 2),
                customer_concentration=CustomerConcentration(
                    top_5_share=round(top_five_share, 2),
                    customers_with_sales=customers_with_sales,
                    leading_customer=leading_name,
                ),
            )
        if header_total_amount <= 0 or not ventas_por_cliente:
            return AnalyticsInsights(
                largest_customer_share=0.0,
                customer_concentration=CustomerConcentration(
                    top_5_share=0.0,
                    customers_with_sales=len(ventas_por_cliente),
                    leading_customer=None,
                ),
            )
        leading = ventas_por_cliente[0]
        largest_share = float(leading.total_ventas / header_total_amount * 100)
        top_five_total = sum(item.total_ventas for item in ventas_por_cliente[:5])
        top_five_share = float(top_five_total / header_total_amount * 100)
        return AnalyticsInsights(
            largest_customer_share=round(largest_share, 2),
            customer_concentration=CustomerConcentration(
                top_5_share=round(top_five_share, 2),
                customers_with_sales=len(ventas_por_cliente),
                leading_customer=leading.nombre or leading.cliente_dynamics_id,
            ),
        )

    @staticmethod
    def _decimal_value(value: Decimal) -> str:
        return format(value, '.2f')
