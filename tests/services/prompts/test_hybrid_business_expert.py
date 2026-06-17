from app.services.prompts.hybrid_business_expert import build_hybrid_business_expert_prompt

def test_build_hybrid_business_expert_prompt_includes_context_and_rules() -> None:
    hybrid_context = {
        'analytics_snapshot': {'summary': {'total_customers': 100}},
        'executive_insights': {'dominant_customer': 'Alpha'},
        'document_context': {'sources': ['Manual_Clientes.pdf']},
        'document_insights': {'confidence_level': 'MEDIUM'},
    }
    hybrid_insights = {
        'cross_source_findings': ['Relacion cliente-documento'],
        'related_documents': ['Manual_Clientes.pdf'],
        'confidence': 'MEDIUM',
    }
    prompt = build_hybrid_business_expert_prompt(
        question='¿Cuántos clientes tenemos y cómo se registran?',
        hybrid_context=hybrid_context,
        hybrid_insights=hybrid_insights,
    )
    assert 'consultor empresarial senior' in prompt
    assert 'CONTEXTO HIBRIDO' in prompt
    assert 'INSIGHTS HIBRIDOS' in prompt
    assert 'cross_source_findings' in prompt
    assert 'No recomiendes acciones' in prompt
