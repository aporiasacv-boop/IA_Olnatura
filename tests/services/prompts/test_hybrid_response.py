from app.services.context_fusion_service import FusedContext
from app.services.prompts.hybrid_response import build_hybrid_response_prompt

def test_build_hybrid_response_prompt_includes_analytics_and_documents() -> None:
    context = FusedContext(
        analytics_intent='sales_average_ticket',
        analytics_data={'average_order_amount': '100.00'},
        document_results=[{'document': 'Proc.docx', 'score': 0.9, 'content': 'Procedimiento de ventas.'}],
    )
    prompt = build_hybrid_response_prompt(
        question='¿Cuál es el ticket promedio y cuál es el procedimiento de ventas?',
        context=context,
    )
    assert 'CONTEXTO FUSIONADO' in prompt
    assert 'sales_average_ticket' in prompt
    assert 'Proc.docx' in prompt
    assert 'procedimiento de ventas' in prompt.lower()

def test_build_hybrid_response_prompt_handles_empty_documents() -> None:
    context = FusedContext(
        analytics_intent='customers_count',
        analytics_data={'total_customers': 50},
        document_results=[],
    )
    prompt = build_hybrid_response_prompt(
        question='¿Cuántos clientes tenemos y cómo se registran?',
        context=context,
    )
    assert '"documents": []' in prompt
