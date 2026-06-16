from app.domain.chat import QuestionCategory
from app.integrations.ollama.protocols import LLMClient
from app.services.analytics_service import AnalyticsService
from app.services.question_classifier import QuestionClassifier

class ChatOrchestratorService:

    def __init__(self, analytics_service: AnalyticsService, llm_client: LLMClient, classifier: QuestionClassifier | None=None):
        self._analytics = analytics_service
        self._llm_client = llm_client
        self._classifier = classifier or QuestionClassifier()

    def answer(self, question: str) -> str:
        category = self._classifier.classify(question)
        if category is QuestionCategory.VENTAS:
            return self._answer_ventas(question)
        if category is QuestionCategory.CLIENTES:
            return self._answer_clientes(question)
        return self._answer_general(question)

    def classify(self, question: str) -> QuestionCategory:
        return self._classifier.classify(question)

    def _answer_ventas(self, question: str) -> str:
        data = self._analytics.total_ventas_mes()
        return f'Las ventas del mes ({data.month:02d}/{data.year}) ascienden a {data.total:,.2f} en {data.cantidad_ventas} operaciones registradas.'

    def _answer_clientes(self, question: str) -> str:
        normalized = question.lower()
        if any((word in normalized for word in ('top', 'mejor', 'mejores', 'principal', 'principales'))):
            top = self._analytics.top_clientes(limit=5)
            if not top:
                return 'No hay datos de clientes disponibles en el sistema.'
            lines = [f'{index}. {item.nombre or item.cliente_dynamics_id}: {item.total_ventas:,.2f} ({item.cantidad_ventas} ventas)' for index, item in enumerate(top, start=1)]
            return 'Top clientes por volumen de ventas:\n' + '\n'.join(lines)
        total = self._analytics.count_clientes()
        return f'El sistema registra {total} clientes activos.'

    def _answer_general(self, question: str) -> str:
        prompt = f'Responde la siguiente pregunta empresarial de forma clara y concisa en español.\nNO recomiendes acciones ni tomes decisiones.\n\nPregunta: {question}'
        return self._llm_client.generate(prompt)
