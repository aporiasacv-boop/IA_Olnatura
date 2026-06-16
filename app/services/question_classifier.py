from dataclasses import dataclass
from typing import Any
import unicodedata
from app.domain.chat import ChatIntent, QuestionCategory

class QuestionClassifier:
    _VENTAS_KEYWORDS = ('venta', 'ventas', 'factur', 'ingreso', 'ingresos', 'monto', 'pedido', 'pedidos', 'orden', 'ordenes', 'facturacion')
    _CLIENTES_KEYWORDS = ('cliente', 'clientes', 'comprador', 'compradores', 'cartera')
    _TOP_KEYWORDS = ('principal', 'principales', 'mejor', 'mejores', 'top')
    _CLIENT_WORDS = ('cliente', 'clientes')
    _DOCUMENT_SIGNAL_KEYWORDS = (
        'procedimiento', 'proceso', 'como se', 'registran', 'registro', 'manual',
        'politica', 'norma', 'documento', 'acta', 'instructivo', 'guia', 'pasos',
        'requisito', 'objeto social', 'contrato', 'reglamento', 'flujo', 'protocolo',
    )

    def classify(self, question: str) -> QuestionCategory:
        normalized = self._normalize(question)
        if any((keyword in normalized for keyword in self._VENTAS_KEYWORDS)):
            return QuestionCategory.VENTAS
        if any((keyword in normalized for keyword in self._CLIENTES_KEYWORDS)):
            return QuestionCategory.CLIENTES
        return QuestionCategory.GENERAL

    def resolve_intent(self, question: str) -> ChatIntent:
        normalized = self._normalize(question)
        if any(keyword in normalized for keyword in self._TOP_KEYWORDS) and any(word in normalized for word in self._CLIENT_WORDS):
            return ChatIntent.TOP_CUSTOMERS
        if 'cuantos clientes' in normalized or 'numero de clientes' in normalized or 'total de clientes' in normalized:
            return ChatIntent.CUSTOMERS_COUNT
        if 'ticket promedio' in normalized or ('promedio' in normalized and any(word in normalized for word in ('pedido', 'pedidos', 'orden', 'ordenes', 'ticket'))):
            return ChatIntent.SALES_AVERAGE_TICKET
        if 'monto total' in normalized or 'total vendido' in normalized or ('total' in normalized and 'vendid' in normalized):
            return ChatIntent.SALES_TOTAL_AMOUNT
        if 'cuantos pedidos' in normalized or 'numero de pedidos' in normalized or 'total de pedidos' in normalized:
            return ChatIntent.SALES_COUNT
        return ChatIntent.UNKNOWN

    def is_hybrid(self, question: str) -> bool:
        intent = self.resolve_intent(question)
        if intent is ChatIntent.UNKNOWN:
            return False
        normalized = self._normalize(question)
        return any(keyword in normalized for keyword in self._DOCUMENT_SIGNAL_KEYWORDS)

    def _normalize(self, question: str) -> str:
        lowered = question.lower().strip()
        return ''.join((character for character in unicodedata.normalize('NFD', lowered) if unicodedata.category(character) != 'Mn'))
