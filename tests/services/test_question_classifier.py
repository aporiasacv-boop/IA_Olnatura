from app.domain.chat import ChatIntent, QuestionCategory
from app.services.question_classifier import QuestionClassifier

def test_classify_ventas_question() -> None:
    classifier = QuestionClassifier()
    assert classifier.classify('¿Cuáles fueron las ventas del mes?') == QuestionCategory.VENTAS

def test_classify_clientes_question() -> None:
    classifier = QuestionClassifier()
    assert classifier.classify('¿Cuántos clientes tenemos?') == QuestionCategory.CLIENTES

def test_classify_general_question() -> None:
    classifier = QuestionClassifier()
    assert classifier.classify('¿Qué es un ERP?') == QuestionCategory.GENERAL

def test_ventas_takes_priority_over_clientes() -> None:
    classifier = QuestionClassifier()
    assert classifier.classify('¿Cuáles clientes generaron más ventas?') == QuestionCategory.VENTAS

def test_resolve_intent_customers_count() -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent('¿Cuántos clientes tenemos?') == ChatIntent.CUSTOMERS_COUNT

def test_resolve_intent_sales_count() -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent('¿Cuántos pedidos tenemos?') == ChatIntent.SALES_COUNT

def test_resolve_intent_sales_total_amount() -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent('¿Cuál es el monto total vendido?') == ChatIntent.SALES_TOTAL_AMOUNT

def test_resolve_intent_average_ticket() -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent('¿Cuál es el ticket promedio?') == ChatIntent.SALES_AVERAGE_TICKET

def test_resolve_intent_top_customers() -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent('¿Quiénes son nuestros principales clientes?') == ChatIntent.TOP_CUSTOMERS

def test_resolve_intent_unknown() -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent('¿Qué es un ERP?') == ChatIntent.UNKNOWN

def test_top_customers_takes_priority_over_customers_count() -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent('¿Cuáles son los mejores clientes?') == ChatIntent.TOP_CUSTOMERS
