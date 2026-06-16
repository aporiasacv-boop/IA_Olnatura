from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from app.domain.chat import ChatIntent
from app.services.analytics_service import AnalyticsService
from app.services.question_classifier import QuestionClassifier

@dataclass(frozen=True)
class ChatResult:
    question: str
    intent: ChatIntent
    data: dict[str, Any] | list[dict[str, Any]] | None

class ChatService:

    def __init__(self, analytics_service: AnalyticsService, classifier: QuestionClassifier | None=None, top_customers_limit: int=10):
        self._analytics = analytics_service
        self._classifier = classifier or QuestionClassifier()
        self._top_customers_limit = top_customers_limit

    def process(self, question: str) -> ChatResult:
        intent = self._classifier.resolve_intent(question)
        data = self._build_data(intent)
        return ChatResult(question=question, intent=intent, data=data)

    def _build_data(self, intent: ChatIntent) -> dict[str, Any] | list[dict[str, Any]] | None:
        if intent is ChatIntent.CUSTOMERS_COUNT:
            return {'total_customers': self._analytics.count_clientes()}
        if intent is ChatIntent.SALES_COUNT:
            return {'total_sales_orders': self._analytics.count_sales_orders()}
        if intent in (ChatIntent.SALES_TOTAL_AMOUNT, ChatIntent.SALES_AVERAGE_TICKET):
            summary = self._analytics.sales_summary()
            return {
                'total_orders': summary.total_orders,
                'total_amount': self._decimal_value(summary.total_amount),
                'average_order_amount': self._decimal_value(summary.average_order_amount),
            }
        if intent is ChatIntent.TOP_CUSTOMERS:
            return [
                {
                    'customer_account': item.customer_account,
                    'customer_name': item.customer_name,
                    'orders': item.orders,
                    'total_amount': self._decimal_value(item.total_amount),
                }
                for item in self._analytics.top_customers(limit=self._top_customers_limit)
            ]
        return None

    @staticmethod
    def _decimal_value(value: Decimal) -> str:
        return format(value, 'f')
