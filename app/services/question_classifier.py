"""
Clasificador de preguntas empresariales.

Identifica si una consulta pertenece a ventas, clientes o general
mediante reglas de palabras clave (desacoplado del orquestador).
"""

from app.domain.chat import QuestionCategory


class QuestionClassifier:
    """Clasifica preguntas en categorías empresariales."""

    _VENTAS_KEYWORDS = (
        "venta",
        "ventas",
        "factur",
        "ingreso",
        "ingresos",
        "monto",
        "pedido",
        "pedidos",
        "orden",
        "ordenes",
        "facturación",
        "facturacion",
    )

    _CLIENTES_KEYWORDS = (
        "cliente",
        "clientes",
        "comprador",
        "compradores",
        "cartera",
    )

    def classify(self, question: str) -> QuestionCategory:
        """
        Determina la categoría de una pregunta.

        Prioridad: ventas > clientes > general.

        Args:
            question: Texto de la pregunta del usuario.

        Returns:
            QuestionCategory correspondiente.
        """
        normalized = question.lower()

        if any(keyword in normalized for keyword in self._VENTAS_KEYWORDS):
            return QuestionCategory.VENTAS

        if any(keyword in normalized for keyword in self._CLIENTES_KEYWORDS):
            return QuestionCategory.CLIENTES

        return QuestionCategory.GENERAL
