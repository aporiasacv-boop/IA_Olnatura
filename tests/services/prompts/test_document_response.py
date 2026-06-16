from app.services.prompts.document_response import build_document_response_prompt

def test_build_document_response_prompt_includes_question_and_fragments() -> None:
    prompt = build_document_response_prompt(
        question='¿Cuál es el objeto social de la empresa?',
        results=[{'document': 'Acta_Constitutiva.docx', 'score': 0.93, 'content': 'El objeto social es comercializar productos naturales.'}],
    )
    assert '¿Cuál es el objeto social de la empresa?' in prompt
    assert 'Acta_Constitutiva.docx' in prompt
    assert 'comercializar productos naturales' in prompt

def test_build_document_response_prompt_includes_guardrails() -> None:
    prompt = build_document_response_prompt(question='¿Cuál es la política?', results=[])
    assert 'NO inventes informacion' in prompt
    assert 'NO recomiendes' in prompt
    assert 'fragmentos proporcionados' in prompt
