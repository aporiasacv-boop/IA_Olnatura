from app.services.prompts.governance_expert import build_governance_expert_prompt

def test_build_governance_expert_prompt_includes_audit_role() -> None:
    prompt = build_governance_expert_prompt(
        question='¿Qué evidencia tienes?',
        answer='Farmacias de Similares concentra 42.2% de los ingresos.',
        governance_context={
            'source_type': 'analytics',
            'source_tables': ['venta_lineas'],
            'confidence_level': 'HIGH',
            'evidence': [{'statement': 'Concentracion comercial', 'evidence': ['100 lineas analizadas']}],
            'limitations': [],
        },
    )
    assert 'auditor empresarial' in prompt
    assert 'Fuente:' in prompt
    assert 'Evidencia:' in prompt
    assert 'Nunca inventes fuentes' in prompt
