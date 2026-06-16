from app.services.prompts.ai_response import build_ai_response_prompt

def test_build_ai_response_prompt_includes_question_intent_and_data() -> None:
    prompt = build_ai_response_prompt(
        question='¿Cuántos clientes tenemos?',
        intent='customers_count',
        data={'total_customers': 100},
    )
    assert '¿Cuántos clientes tenemos?' in prompt
    assert 'customers_count' in prompt
    assert '"total_customers": 100' in prompt

def test_build_ai_response_prompt_includes_guardrails() -> None:
    prompt = build_ai_response_prompt(
        question='¿Cuál es el ticket promedio?',
        intent='sales_average_ticket',
        data={'average_order_amount': '1100.00'},
    )
    assert 'NO consultes bases de datos' in prompt
    assert 'NO recomiendes' in prompt
    assert 'SOLO interpreta' in prompt
    assert 'Dynamics 365 Finance & Operations' in prompt

def test_build_ai_response_prompt_handles_null_data() -> None:
    prompt = build_ai_response_prompt(
        question='¿Qué es un ERP?',
        intent='unknown',
        data=None,
    )
    assert 'null' in prompt
    assert 'unknown' in prompt
