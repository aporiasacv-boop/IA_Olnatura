import unicodedata
from app.domain.chat import ChatIntent, QuestionCategory

class QuestionClassifier:
    _VENTAS_KEYWORDS = ('venta', 'ventas', 'factur', 'ingreso', 'ingresos', 'monto', 'pedido', 'pedidos', 'orden', 'ordenes', 'facturacion')
    _CLIENTES_KEYWORDS = ('cliente', 'clientes', 'comprador', 'compradores', 'cartera')
    _TOP_KEYWORDS = ('principal', 'principales', 'mejor', 'mejores', 'top')
    _CLIENT_WORDS = ('cliente', 'clientes')
    _TOP_CUSTOMERS_PHRASES = (
        'top clientes',
        'clientes top',
        'mejores clientes',
        'clientes mejores',
        'principales clientes',
        'clientes principales',
        'clientes mas importantes',
        'clientes importantes',
        'cliente que mas compra',
        'cliente que mas compran',
        'clientes que mas compran',
        'quien compra mas',
        'quienes compran mas',
        'quien es el cliente que mas compra',
        'cual es el cliente que mas compra',
    )
    _DOCUMENT_SIGNAL_KEYWORDS = (
        'procedimiento', 'proceso', 'como se', 'registran', 'registro', 'manual',
        'politica', 'norma', 'documento', 'acta', 'instructivo', 'guia', 'pasos',
        'requisito', 'objeto social', 'contrato', 'reglamento', 'flujo', 'protocolo',
    )
    _EXECUTIVE_ANALYTICS_PHRASES = (
        'como esta distribuida',
        'distribucion de la cartera',
        'distribuida nuestra cartera',
        'concentra mas compras',
        'concentran mas',
        'mas relevantes',
        'analisis de ventas',
        'panorama de ventas',
        'como van las ventas',
        'que puedes decir de las ventas',
        'que me dices de las ventas',
        'cuanto hemos vendido',
        'cuanto hemos facturado',
        'genera mas ingresos',
        'productos venden mas',
        'producto concentra',
        'distribuido el ingreso',
        'distribucion del ingreso',
        'mayor facturacion',
    )
    _EXECUTIVE_PHRASES = (
        'dame un resumen ejecutivo',
        'resumen ejecutivo',
        'que observas en las ventas',
        'que hallazgos importantes ves',
        'hallazgos importantes',
        'hay riesgos comerciales',
        'riesgos comerciales',
        'dependemos de pocos clientes',
        'existe concentracion comercial',
        'concentracion comercial',
        'que te llama la atencion',
        'que observas',
        'que hallazgos ves',
        'que te llama la atencion de las ventas',
    )

    _ADVANCED_HYBRID_PHRASES = (
        'cuantos clientes tenemos y como se registran',
        'cliente genera mas ingresos y cual es el procedimiento',
        'cliente genera mas ingresos y que documentacion',
        'producto principal y que documentacion existe',
        'producto principal y que documentacion',
        'observas en ventas considerando los procedimientos',
        'riesgos comerciales observas y que documentos',
        'riesgos comerciales y que documentos',
        'metricas y procedimiento',
        'ingresos y procedimiento',
        'ingresos y documentacion',
    )

    _ANALYTICS_INTENTS = frozenset({
        ChatIntent.CUSTOMERS_COUNT,
        ChatIntent.SALES_COUNT,
        ChatIntent.SALES_TOTAL_AMOUNT,
        ChatIntent.SALES_AVERAGE_TICKET,
        ChatIntent.TOP_CUSTOMERS,
    })

    def classify(self, question: str) -> QuestionCategory:
        normalized = self._normalize(question)
        if any((keyword in normalized for keyword in self._VENTAS_KEYWORDS)):
            return QuestionCategory.VENTAS
        if any((keyword in normalized for keyword in self._CLIENTES_KEYWORDS)):
            return QuestionCategory.CLIENTES
        return QuestionCategory.GENERAL

    def resolve_intent(self, question: str) -> ChatIntent:
        normalized = self._normalize(question)
        if self._is_top_customers_intent(normalized):
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

    def is_executive_question(self, question: str) -> bool:
        normalized = self._normalize(question)
        if any(phrase in normalized for phrase in self._EXECUTIVE_PHRASES):
            return True
        if 'resumen' in normalized and 'ejecutivo' in normalized:
            return True
        if 'riesgo' in normalized and any(token in normalized for token in ('comercial', 'comerciales', 'venta', 'ventas')):
            return True
        if 'dependemos' in normalized and 'cliente' in normalized:
            return True
        return False

    def is_analytics_question(self, question: str) -> bool:
        if self.is_executive_question(question):
            return True
        if self.resolve_intent(question) in self._ANALYTICS_INTENTS:
            return True
        normalized = self._normalize(question)
        if any(phrase in normalized for phrase in self._EXECUTIVE_ANALYTICS_PHRASES):
            return True
        if 'cartera' in normalized and any(token in normalized for token in ('distribu', 'como esta', 'panorama')):
            return True
        if 'resumen' in normalized and any(token in normalized for token in ('venta', 'ventas', 'ejecutivo')):
            return True
        return False

    def is_advanced_hybrid(self, question: str) -> bool:
        normalized = self._normalize(question)
        if any(phrase in normalized for phrase in self._ADVANCED_HYBRID_PHRASES):
            return True
        if 'genera mas ingresos' in normalized and any(token in normalized for token in ('procedimiento', 'documentacion', 'manual')):
            return True
        if 'producto principal' in normalized and 'documentacion' in normalized:
            return True
        if 'riesgos comerciales' in normalized and 'documento' in normalized:
            return True
        if 'observas' in normalized and 'venta' in normalized and any(token in normalized for token in ('procedimiento', 'manual', 'documento')):
            return True
        return False

    def is_hybrid(self, question: str) -> bool:
        if self.is_advanced_hybrid(question):
            return True
        if not (self.is_analytics_question(question) or self.is_executive_question(question)):
            return False
        normalized = self._normalize(question)
        return any(keyword in normalized for keyword in self._DOCUMENT_SIGNAL_KEYWORDS)

    def _is_top_customers_intent(self, normalized: str) -> bool:
        if any(phrase in normalized for phrase in self._TOP_CUSTOMERS_PHRASES):
            return True
        if any(keyword in normalized for keyword in self._TOP_KEYWORDS) and any(word in normalized for word in self._CLIENT_WORDS):
            return True
        if 'importante' in normalized and any(word in normalized for word in self._CLIENT_WORDS):
            return True
        if ('mas compra' in normalized or 'mas compran' in normalized) and any(word in normalized for word in self._CLIENT_WORDS):
            return True
        if 'muestrame' in normalized and any(word in normalized for word in self._CLIENT_WORDS):
            if any(keyword in normalized for keyword in (*self._TOP_KEYWORDS, 'importante', 'importantes')):
                return True
        return False

    def _normalize(self, question: str) -> str:
        lowered = question.lower().strip()
        return ''.join((character for character in unicodedata.normalize('NFD', lowered) if unicodedata.category(character) != 'Mn'))
