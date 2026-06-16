from app.rag.prompts import build_rag_prompt

def test_build_rag_prompt_includes_context_and_question() -> None:
    prompt = build_rag_prompt('Contexto empresarial', '¿Cuál es la meta?')
    assert 'Contexto empresarial' in prompt
    assert '¿Cuál es la meta?' in prompt
    assert 'ÚNICAMENTE el contexto' in prompt
