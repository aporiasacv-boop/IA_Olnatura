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
