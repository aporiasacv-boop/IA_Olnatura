from app.domain.chat import ChatIntent, QuestionCategory
from app.services.question_classifier import QuestionClassifier
import pytest

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

def test_is_hybrid_when_analytics_intent_and_document_signal() -> None:
    classifier = QuestionClassifier()
    assert classifier.is_hybrid('¿Cuántos clientes tenemos y cómo se registran?') is True
    assert classifier.is_hybrid('¿Cuál es el ticket promedio y cuál es el procedimiento de ventas?') is True

def test_is_hybrid_false_for_analytics_only() -> None:
    classifier = QuestionClassifier()
    assert classifier.is_hybrid('¿Cuántos clientes tenemos?') is False

def test_is_hybrid_false_for_documents_only() -> None:
    classifier = QuestionClassifier()
    assert classifier.is_hybrid('¿Cuál es el procedimiento de ventas?') is False

@pytest.mark.parametrize('question', [
    '¿Cuántos clientes tenemos y cómo se registran?',
    '¿Qué cliente genera más ingresos y cuál es el procedimiento para gestionarlo?',
    '¿Cuál es nuestro producto principal y qué documentación existe?',
    '¿Qué observas en ventas considerando los procedimientos actuales?',
    '¿Qué riesgos comerciales observas y qué documentos los respaldan?',
])
def test_is_advanced_hybrid_detects_complex_questions(question: str) -> None:
    classifier = QuestionClassifier()
    assert classifier.is_advanced_hybrid(question) is True
    assert classifier.is_hybrid(question) is True

@pytest.mark.parametrize('question', [
    '¿Qué debería revisar?',
    '¿Qué me recomiendas analizar?',
    '¿Dónde debería poner atención?',
    '¿Qué riesgos debería monitorear?',
    '¿Qué temas requieren seguimiento?',
])
def test_is_copilot_question_detects_copilot_prompts(question: str) -> None:
    classifier = QuestionClassifier()
    assert classifier.is_copilot_question(question) is True

@pytest.mark.parametrize('question', [
    '¿Cómo está distribuida nuestra cartera?',
    '¿Qué observas en las ventas?',
    'Dame un resumen ejecutivo de ventas',
    '¿Quién concentra más compras?',
])
def test_is_analytics_question_for_executive_prompts(question: str) -> None:
    classifier = QuestionClassifier()
    assert classifier.is_analytics_question(question) is True
    assert classifier.resolve_intent(question) in (ChatIntent.UNKNOWN, ChatIntent.TOP_CUSTOMERS)

@pytest.mark.parametrize('question', [
    '¿Cuál es el cliente que más compra?',
    'Muéstrame los clientes más importantes',
    'Clientes principales',
    'Mejores clientes',
    'Top clientes',
])
def test_resolve_intent_top_customers_synonyms(question: str) -> None:
    classifier = QuestionClassifier()
    assert classifier.resolve_intent(question) == ChatIntent.TOP_CUSTOMERS

@pytest.mark.parametrize('question', [
    'Dame un resumen ejecutivo',
    '¿Qué observas en las ventas?',
    '¿Qué hallazgos importantes ves?',
    '¿Hay riesgos comerciales?',
    '¿Dependemos de pocos clientes?',
    '¿Existe concentración comercial?',
    '¿Qué te llama la atención?',
])
def test_is_executive_question_detects_executive_prompts(question: str) -> None:
    classifier = QuestionClassifier()
    assert classifier.is_executive_question(question) is True

def test_is_executive_question_false_for_metric_questions() -> None:
    classifier = QuestionClassifier()
    assert classifier.is_executive_question('¿Cuántos clientes tenemos?') is False
    assert classifier.is_executive_question('¿Cuál es el monto total vendido?') is False

def test_executive_question_is_also_analytics_question() -> None:
    classifier = QuestionClassifier()
    assert classifier.is_executive_question('Dame un resumen ejecutivo') is True
    assert classifier.is_analytics_question('Dame un resumen ejecutivo') is True

@pytest.mark.parametrize('question', [
    '¿Qué ha cambiado?',
    '¿Qué diferencias observas?',
    '¿Hay cambios respecto al análisis anterior?',
    '¿Qué hallazgos siguen presentes?',
])
def test_is_memory_question_detects_memory_prompts(question: str) -> None:
    classifier = QuestionClassifier()
    assert classifier.is_memory_question(question) is True

def test_memory_question_is_not_executive_question() -> None:
    classifier = QuestionClassifier()
    assert classifier.is_memory_question('¿Qué ha cambiado?') is True
    assert classifier.is_executive_question('¿Qué ha cambiado?') is False
