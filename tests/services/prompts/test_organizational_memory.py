from app.services.prompts.organizational_memory import build_organizational_memory_prompt


def test_build_organizational_memory_prompt_includes_role_and_context() -> None:
    prompt = build_organizational_memory_prompt(
        question='¿Qué ha cambiado?',
        memory_context={
            'latest_snapshot': {'total_customers': 100},
            'previous_snapshot': {'total_customers': 100},
            'memory_insights': {'changes': [], 'stable_findings': ['Estable'], 'new_findings': []},
        },
    )
    assert 'historiador empresarial' in prompt
    assert '¿Qué ha cambiado?' in prompt
    assert 'memory_insights' in prompt
    assert 'No recomiendes acciones' in prompt
