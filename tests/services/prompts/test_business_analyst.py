from app.services.prompts.business_analyst import build_business_analyst_prompt

def test_build_business_analyst_prompt_includes_snapshot_and_rules() -> None:
    snapshot = {
        'summary': {'total_customers': 100, 'total_orders': 100},
        'insights': {'largest_customer_share': 42.5},
    }
    prompt = build_business_analyst_prompt(
        question='Dame un resumen ejecutivo de ventas',
        snapshot=snapshot,
    )
    assert 'analista empresarial senior' in prompt
    assert 'SNAPSHOT EMPRESARIAL' in prompt
    assert 'total_customers' in prompt
    assert 'financials' in prompt
    assert 'total_revenue' in prompt
    assert 'No recomiendes acciones estrategicas' in prompt
    assert 'Dame un resumen ejecutivo de ventas' in prompt
