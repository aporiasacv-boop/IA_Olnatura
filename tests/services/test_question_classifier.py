"""
Pruebas del clasificador de preguntas empresariales.
"""

from app.domain.chat import QuestionCategory
from app.services.question_classifier import QuestionClassifier


def test_classify_ventas_question() -> None:
    """Verifica clasificación de preguntas sobre ventas."""
    classifier = QuestionClassifier()
    assert classifier.classify("¿Cuáles fueron las ventas del mes?") == QuestionCategory.VENTAS


def test_classify_clientes_question() -> None:
    """Verifica clasificación de preguntas sobre clientes."""
    classifier = QuestionClassifier()
    assert classifier.classify("¿Cuántos clientes tenemos?") == QuestionCategory.CLIENTES


def test_classify_general_question() -> None:
    """Verifica clasificación de preguntas generales."""
    classifier = QuestionClassifier()
    assert classifier.classify("¿Qué es un ERP?") == QuestionCategory.GENERAL


def test_ventas_takes_priority_over_clientes() -> None:
    """Verifica que ventas tiene prioridad si ambas palabras clave aparecen."""
    classifier = QuestionClassifier()
    assert (
        classifier.classify("¿Cuáles clientes generaron más ventas?")
        == QuestionCategory.VENTAS
    )
