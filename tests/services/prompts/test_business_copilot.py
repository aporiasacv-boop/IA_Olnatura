from app.services.prompts.business_copilot import build_business_copilot_prompt

def test_build_business_copilot_prompt_includes_context_and_rules() -> None:
    copilot_context = {
        'analytics_snapshot': {'summary': {'total_customers': 100}},
        'executive_insights': {'dominant_customer': 'Alpha'},
        'hybrid_insights': {'confidence': 'MEDIUM'},
        'copilot_insights': {
            'observations': ['Concentracion moderada'],
            'attention_points': ['Dependencia de clientes'],
            'recommended_reviews': ['Revisar periodicamente la dependencia de los principales clientes.'],
        },
    }
    prompt = build_business_copilot_prompt(
        question='¿Qué debería revisar?',
        copilot_context=copilot_context,
    )
    assert 'Business Copilot' in prompt
    assert 'asistente empresarial' in prompt
    assert 'copilot_insights' in prompt
    assert 'No tomes decisiones' in prompt
    assert '¿Qué debería revisar?' in prompt
