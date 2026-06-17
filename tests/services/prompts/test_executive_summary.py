from app.services.prompts.executive_summary import build_executive_summary_prompt

def test_build_executive_summary_prompt_includes_snapshot_and_rules() -> None:
    snapshot = {
        'summary': {'total_orders': 67},
        'financials': {'total_revenue': '49722777.13'},
        'executive_insights': {
            'top_customer_share': 42.2,
            'risk_flags': ['Concentracion comercial moderada'],
        },
    }
    prompt = build_executive_summary_prompt(
        question='Dame un resumen ejecutivo',
        snapshot=snapshot,
    )
    assert 'Director Comercial' in prompt
    assert 'SNAPSHOT EMPRESARIAL' in prompt
    assert 'executive_insights' in prompt
    assert 'financials' in prompt
    assert 'No recomiendes estrategias' in prompt
    assert 'Dame un resumen ejecutivo' in prompt
