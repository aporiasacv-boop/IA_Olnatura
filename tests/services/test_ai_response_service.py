from unittest.mock import MagicMock
from app.services.ai_response_service import AIResponseService

def test_generate_builds_prompt_and_calls_llm() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'Actualmente existen 100 clientes sincronizados.'
    service = AIResponseService(llm)
    answer = service.generate(
        question='¿Cuántos clientes tenemos?',
        intent='customers_count',
        data={'total_customers': 100},
    )
    assert answer == 'Actualmente existen 100 clientes sincronizados.'
    llm.generate.assert_called_once()
    prompt = llm.generate.call_args.args[0]
    assert 'customers_count' in prompt
    assert '"total_customers": 100' in prompt

def test_build_prompt_exposes_prompt_builder() -> None:
    llm = MagicMock()
    service = AIResponseService(llm)
    prompt = service.build_prompt(
        question='¿Cuántos pedidos tenemos?',
        intent='sales_count',
        data={'total_sales_orders': 5},
    )
    assert 'sales_count' in prompt
    assert '"total_sales_orders": 5' in prompt

def test_generate_from_documents_builds_document_prompt() -> None:
    llm = MagicMock()
    llm.generate.return_value = 'El objeto social es comercializar productos naturales.'
    service = AIResponseService(llm)
    answer = service.generate_from_documents(
        question='¿Cuál es el objeto social?',
        results=[{'document': 'Acta.docx', 'score': 0.9, 'content': 'Objeto social...'}],
    )
    assert 'comercializar' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'FRAGMENTOS DOCUMENTALES' in prompt

def test_generate_hybrid_builds_fused_prompt() -> None:
    from app.services.context_fusion_service import FusedContext
    llm = MagicMock()
    llm.generate.return_value = 'Hay 100 clientes y se registran en ventas.'
    service = AIResponseService(llm)
    context = FusedContext(
        analytics_intent='customers_count',
        analytics_data={'total_customers': 100},
        document_results=[{'document': 'Manual.pdf', 'score': 0.9, 'content': 'Registro en ventas.'}],
    )
    answer = service.generate_hybrid(question='¿Cuántos clientes tenemos y cómo se registran?', context=context)
    assert '100 clientes' in answer
    prompt = llm.generate.call_args.args[0]
    assert 'CONTEXTO FUSIONADO' in prompt
    assert 'customers_count' in prompt
    assert 'Manual.pdf' in prompt
